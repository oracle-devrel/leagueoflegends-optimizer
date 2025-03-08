"""
Riot Games API client for the League Optimizer.

This module provides a client for interacting with the Riot Games API
with proper error handling, rate limiting, and retry mechanisms.
"""
import time
from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from leagueoptimizer.config.settings import CONFIG
from leagueoptimizer.utils.logging import api_logger as logger


class RiotAPIError(Exception):
    """Base exception for Riot API errors."""
    pass


class RateLimitExceededError(RiotAPIError):
    """Exception raised when the rate limit is exceeded."""
    pass


class RiotAPIClient:
    """Client for interacting with the Riot Games API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        regions: Optional[List[str]] = None,
        max_retries: int = 3,
        retry_delay: int = 2,
        timeout: int = 10,
    ):
        """
        Initialize the Riot API client.
        
        Args:
            api_key: The Riot API key
            regions: The list of valid regions
            max_retries: The maximum number of retries for failed requests
            retry_delay: The delay between retries in seconds
            timeout: The request timeout in seconds
        """
        config = CONFIG["riot_api"]
        
        self.api_key = api_key or config["key"]
        if not self.api_key:
            raise ValueError("Riot API key is required")
        
        self.regions = regions or config["regions"]
        self.headers = config["headers"].copy()
        self.headers["X-Riot-Token"] = self.api_key
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Rate limiting
        self.request_count = 0
        self.request_limit = config["request_limit_per_minute"]
        self.request_window_start = time.time()
    
    def _check_rate_limit(self) -> None:
        """
        Check if the rate limit has been exceeded.
        
        Raises:
            RateLimitExceededError: If the rate limit is exceeded
        """
        current_time = time.time()
        window_duration = current_time - self.request_window_start
        
        # Reset the window if it's been more than a minute
        if window_duration >= 60:
            self.request_window_start = current_time
            self.request_count = 0
            return
        
        # Check if we've exceeded the rate limit
        if self.request_count >= self.request_limit:
            sleep_time = 60 - window_duration
            logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            
            # Reset the window
            self.request_window_start = time.time()
            self.request_count = 0
    
    def _make_request(
        self, method: str, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Riot API with retry logic.
        
        Args:
            method: The HTTP method (GET, POST, etc.)
            url: The request URL
            params: The request parameters
            
        Returns:
            The JSON response
            
        Raises:
            RiotAPIError: If the request fails after max_retries
        """
        self._check_rate_limit()
        
        retries = 0
        while retries < self.max_retries:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout,
                )
                
                self.request_count += 1
                
                # Handle rate limiting from the API
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                    logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                
                # Handle other error codes
                if response.status_code >= 400:
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    # Don't retry for client errors (except rate limiting)
                    if response.status_code >= 400 and response.status_code < 500:
                        raise RiotAPIError(error_msg)
                    
                    retries += 1
                    if retries < self.max_retries:
                        time.sleep(self.retry_delay)
                    continue
                
                return response.json()
            
            except (ConnectionError, Timeout) as e:
                retries += 1
                logger.warning(f"Request failed (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
            
            except RequestException as e:
                logger.error(f"Request exception: {e}")
                raise RiotAPIError(f"Request failed: {e}")
        
        raise RiotAPIError(f"Failed to make request after {self.max_retries} attempts")
    
    def get_summoner_by_name(self, summoner_name: str, region: str) -> Dict[str, Any]:
        """
        Get summoner information by name.
        
        Args:
            summoner_name: The summoner name
            region: The region
            
        Returns:
            The summoner information
            
        Raises:
            RiotAPIError: If the request fails
        """
        if region not in self.regions:
            raise ValueError(f"Invalid region: {region}")
        
        url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
        return self._make_request("GET", url)
    
    def get_puuid(self, summoner_name: str, region: str, request_region: str = "europe") -> str:
        """
        Get the PUUID for a summoner.
        
        Args:
            summoner_name: The summoner name
            region: The region tag (e.g., "EUW")
            request_region: The request region (europe, americas, asia)
            
        Returns:
            The PUUID
            
        Raises:
            RiotAPIError: If the request fails
        """
        url = f"https://{request_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{region}"
        response = self._make_request("GET", url)
        return response.get("puuid")
    
    def get_champion_mastery(self, encrypted_summoner_id: str, region: str) -> List[Dict[str, Any]]:
        """
        Get champion mastery information for a summoner.
        
        Args:
            encrypted_summoner_id: The encrypted summoner ID
            region: The region
            
        Returns:
            The champion mastery information
            
        Raises:
            RiotAPIError: If the request fails
        """
        if region not in self.regions:
            raise ValueError(f"Invalid region: {region}")
        
        url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}"
        return self._make_request("GET", url)
    
    def get_match_ids(
        self, puuid: str, region: str, queue: Optional[int] = None, count: int = 100
    ) -> List[str]:
        """
        Get match IDs for a player.
        
        Args:
            puuid: The player's PUUID
            region: The region
            queue: The queue ID (optional)
            count: The number of matches to retrieve
            
        Returns:
            The list of match IDs
            
        Raises:
            RiotAPIError: If the request fails
        """
        # Map region to regional routing value
        regional_routing = {
            "br1": "americas",
            "la1": "americas",
            "la2": "americas",
            "na1": "americas",
            "eun1": "europe",
            "euw1": "europe",
            "tr1": "europe",
            "ru": "europe",
            "jp1": "asia",
            "kr": "asia",
            "oc1": "sea",
        }
        
        routing = regional_routing.get(region, "europe")
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        
        params = {"count": count}
        if queue is not None:
            params["queue"] = queue
        
        return self._make_request("GET", url, params)
    
    def get_match(self, match_id: str, region: str) -> Dict[str, Any]:
        """
        Get match information.
        
        Args:
            match_id: The match ID
            region: The region
            
        Returns:
            The match information
            
        Raises:
            RiotAPIError: If the request fails
        """
        # Map region to regional routing value
        regional_routing = {
            "br1": "americas",
            "la1": "americas",
            "la2": "americas",
            "na1": "americas",
            "eun1": "europe",
            "euw1": "europe",
            "tr1": "europe",
            "ru": "europe",
            "jp1": "asia",
            "kr": "asia",
            "oc1": "sea",
        }
        
        routing = regional_routing.get(region, "europe")
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        return self._make_request("GET", url)
    
    def get_match_timeline(self, match_id: str, region: str) -> Dict[str, Any]:
        """
        Get match timeline information.
        
        Args:
            match_id: The match ID
            region: The region
            
        Returns:
            The match timeline information
            
        Raises:
            RiotAPIError: If the request fails
        """
        # Map region to regional routing value
        regional_routing = {
            "br1": "americas",
            "la1": "americas",
            "la2": "americas",
            "na1": "americas",
            "eun1": "europe",
            "euw1": "europe",
            "tr1": "europe",
            "ru": "europe",
            "jp1": "asia",
            "kr": "asia",
            "oc1": "sea",
        }
        
        routing = regional_routing.get(region, "europe")
        url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
        return self._make_request("GET", url)
    
    def get_challenger_league(self, region: str, queue: str = "RANKED_SOLO_5x5") -> Dict[str, Any]:
        """
        Get challenger league information.
        
        Args:
            region: The region
            queue: The queue type
            
        Returns:
            The challenger league information
            
        Raises:
            RiotAPIError: If the request fails
        """
        if region not in self.regions:
            raise ValueError(f"Invalid region: {region}")
        
        url = f"https://{region}.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/{queue}"
        return self._make_request("GET", url)
    
    def get_grandmaster_league(self, region: str, queue: str = "RANKED_SOLO_5x5") -> Dict[str, Any]:
        """
        Get grandmaster league information.
        
        Args:
            region: The region
            queue: The queue type
            
        Returns:
            The grandmaster league information
            
        Raises:
            RiotAPIError: If the request fails
        """
        if region not in self.regions:
            raise ValueError(f"Invalid region: {region}")
        
        url = f"https://{region}.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/{queue}"
        return self._make_request("GET", url)
    
    def get_master_league(self, region: str, queue: str = "RANKED_SOLO_5x5") -> Dict[str, Any]:
        """
        Get master league information.
        
        Args:
            region: The region
            queue: The queue type
            
        Returns:
            The master league information
            
        Raises:
            RiotAPIError: If the request fails
        """
        if region not in self.regions:
            raise ValueError(f"Invalid region: {region}")
        
        url = f"https://{region}.api.riotgames.com/lol/league/v4/masterleagues/by-queue/{queue}"
        return self._make_request("GET", url)


# Singleton client instance
riot_client = RiotAPIClient() 