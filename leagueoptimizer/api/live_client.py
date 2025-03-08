"""
Live Client API module for the League Optimizer.

This module provides functionality for interacting with the League of Legends
Live Client Data API, which provides real-time game data.
"""
import json
import time
from typing import Any, Dict, List, Optional, Union

import requests
from requests.exceptions import ConnectionError, RequestException, Timeout

from leagueoptimizer.config.settings import CONFIG
from leagueoptimizer.utils.logging import api_logger as logger
from leagueoptimizer.utils.message_queue import get_message_queue


class LiveClientError(Exception):
    """Base exception for Live Client API errors."""
    pass


class LiveClientAPI:
    """Client for interacting with the League of Legends Live Client Data API."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        request_interval: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: int = 2,
        timeout: int = 5,
    ):
        """
        Initialize the Live Client API.
        
        Args:
            base_url: The base URL for the Live Client API
            request_interval: The interval between requests in seconds
            max_retries: The maximum number of retries for failed requests
            retry_delay: The delay between retries in seconds
            timeout: The request timeout in seconds
        """
        config = CONFIG["live_client"]
        
        self.base_url = base_url or config["base_url"]
        self.request_interval = request_interval or config["request_interval"]
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        
        # Disable SSL warnings for localhost connections
        requests.packages.urllib3.disable_warnings()
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a request to the Live Client API with retry logic.
        
        Args:
            endpoint: The API endpoint
            
        Returns:
            The JSON response
            
        Raises:
            LiveClientError: If the request fails after max_retries
        """
        url = f"{self.base_url}/{endpoint}"
        
        retries = 0
        while retries < self.max_retries:
            try:
                response = requests.get(
                    url=url,
                    timeout=self.timeout,
                    verify=False,  # Disable SSL verification for localhost
                )
                
                if response.status_code == 404:
                    raise LiveClientError("Game is not in progress")
                
                if response.status_code >= 400:
                    error_msg = f"API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
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
                raise LiveClientError(f"Request failed: {e}")
        
        raise LiveClientError(f"Failed to make request after {self.max_retries} attempts")
    
    def get_all_game_data(self) -> Dict[str, Any]:
        """
        Get all game data from the Live Client API.
        
        Returns:
            All game data
            
        Raises:
            LiveClientError: If the request fails
        """
        return self._make_request("allgamedata")
    
    def get_active_player(self) -> Dict[str, Any]:
        """
        Get active player data from the Live Client API.
        
        Returns:
            Active player data
            
        Raises:
            LiveClientError: If the request fails
        """
        return self._make_request("activeplayer")
    
    def get_player_list(self) -> List[Dict[str, Any]]:
        """
        Get player list data from the Live Client API.
        
        Returns:
            Player list data
            
        Raises:
            LiveClientError: If the request fails
        """
        return self._make_request("playerlist")
    
    def get_events(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get events data from the Live Client API.
        
        Returns:
            Events data
            
        Raises:
            LiveClientError: If the request fails
        """
        return self._make_request("eventdata")
    
    def get_game_stats(self) -> Dict[str, Any]:
        """
        Get game stats data from the Live Client API.
        
        Returns:
            Game stats data
            
        Raises:
            LiveClientError: If the request fails
        """
        return self._make_request("gamestats")
    
    def process_game_data(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process game data to extract relevant information.
        
        Args:
            game_data: The game data from the Live Client API
            
        Returns:
            Processed game data
        """
        # Remove items to avoid quotation mark issues in JSON serialization
        for player in game_data.get("allPlayers", []):
            if "items" in player:
                del player["items"]
        
        # Extract only the necessary data
        processed_data = {
            "activePlayer": game_data.get("activePlayer", {}),
            "allPlayers": game_data.get("allPlayers", []),
            "gameData": game_data.get("gameData", {}),
        }
        
        return processed_data
    
    def extract_prediction_features(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features for prediction from game data.
        
        Args:
            game_data: The game data from the Live Client API
            
        Returns:
            Features for prediction
        """
        active_player = game_data.get("activePlayer", {})
        champion_stats = active_player.get("championStats", {})
        game_time = game_data.get("gameData", {}).get("gameTime", 0)
        
        # Extract features used by the prediction model
        features = {
            "magicResist": champion_stats.get("magicResist", 0),
            "healthRegenRate": champion_stats.get("healthRegenRate", 0),
            "spellVamp": champion_stats.get("spellVamp", 0),
            "timestamp": int(game_time * 1000),  # Convert to milliseconds
            "maxHealth": champion_stats.get("maxHealth", 0),
            "moveSpeed": champion_stats.get("moveSpeed", 0),
            "attackDamage": champion_stats.get("attackDamage", 0),
            "armorPenetrationPercent": champion_stats.get("armorPenetrationPercent", 0),
            "lifesteal": champion_stats.get("lifeSteal", 0),
            "abilityPower": champion_stats.get("abilityPower", 0),
            "resourceValue": champion_stats.get("resourceValue", 0),
            "magicPenetrationFlat": champion_stats.get("magicPenetrationFlat", 0),
            "attackSpeed": champion_stats.get("attackSpeed", 0),
            "currentHealth": champion_stats.get("currentHealth", 0),
            "armor": champion_stats.get("armor", 0),
            "magicPenetrationPercent": champion_stats.get("magicPenetrationPercent", 0),
            "resourceMax": champion_stats.get("resourceMax", 0),
            "resourceRegenRate": champion_stats.get("resourceRegenRate", 0),
        }
        
        return features


class LiveClientProducer:
    """Producer for the Live Client API that publishes data to a message queue."""
    
    def __init__(
        self,
        api: Optional[LiveClientAPI] = None,
        queue_name: Optional[str] = None,
        request_interval: Optional[int] = None,
    ):
        """
        Initialize the Live Client Producer.
        
        Args:
            api: The Live Client API instance
            queue_name: The name of the message queue
            request_interval: The interval between requests in seconds
        """
        self.api = api or LiveClientAPI()
        self.request_interval = request_interval or self.api.request_interval
        self.queue = get_message_queue(queue_name)
    
    def start(self) -> None:
        """
        Start the producer loop.
        
        This method will continuously poll the Live Client API and publish
        data to the message queue until interrupted.
        """
        logger.info("Starting Live Client Producer")
        self.queue.connect()
        
        try:
            while True:
                try:
                    # Get game data
                    game_data = self.api.get_all_game_data()
                    
                    # Process game data
                    processed_data = self.api.process_game_data(game_data)
                    
                    # Publish to message queue
                    self.queue.publish(processed_data)
                    logger.info("Published game data to message queue")
                
                except LiveClientError as e:
                    logger.warning(f"Live Client error: {e}")
                
                # Wait for the next request
                time.sleep(self.request_interval)
        
        except KeyboardInterrupt:
            logger.info("Stopping Live Client Producer")
        
        finally:
            self.queue.disconnect()


class LiveClientConsumer:
    """Consumer for the Live Client API that processes data from a message queue."""
    
    def __init__(
        self,
        queue_name: Optional[str] = None,
        model_path: Optional[str] = None,
    ):
        """
        Initialize the Live Client Consumer.
        
        Args:
            queue_name: The name of the message queue
            model_path: The path to the trained model
        """
        self.queue = get_message_queue(queue_name)
        self.model_path = model_path or CONFIG["model"]["save_path"]
        self.api = LiveClientAPI()
        
        # Lazy-load the model when needed
        self._predictor = None
    
    @property
    def predictor(self):
        """Get the predictor, loading it if necessary."""
        if self._predictor is None:
            try:
                from autogluon.tabular import TabularPredictor
                self._predictor = TabularPredictor.load(self.model_path)
                logger.info(f"Loaded model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
        return self._predictor
    
    def process_message(self, message: str) -> None:
        """
        Process a message from the queue.
        
        Args:
            message: The message from the queue
        """
        try:
            # Parse the message
            game_data = json.loads(message)
            
            # Extract features for prediction
            features = self.api.extract_prediction_features(game_data)
            
            # Convert to DataFrame for prediction
            import pandas as pd
            sample_df = pd.DataFrame([features])
            
            # Make prediction
            prediction = self.predictor.predict(sample_df)
            pred_probs = self.predictor.predict_proba(sample_df)
            
            # Log the prediction
            expected_result = prediction.get(0)
            if expected_result == 0:
                logger.info(f"Expected LOSS, {pred_probs.iloc[0][0] * 100:.2f}% probable")
            else:
                logger.info(f"Expected WIN, {pred_probs.iloc[0][1] * 100:.2f}% probable")
            
            logger.info(
                f"Win/loss probability: {pred_probs.iloc[0][1] * 100:.2f}%/{pred_probs.iloc[0][0] * 100:.2f}%"
            )
            
            # Log team information
            for player in game_data.get("allPlayers", []):
                team_color = "blue" if player.get("team") == "ORDER" else "red"
                logger.debug(f"Team {team_color}: {player.get('championName')}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def start(self) -> None:
        """
        Start the consumer loop.
        
        This method will continuously consume messages from the queue
        and process them until interrupted.
        """
        logger.info("Starting Live Client Consumer")
        self.queue.connect()
        
        try:
            self.queue.consume(self.process_message)
        
        except KeyboardInterrupt:
            logger.info("Stopping Live Client Consumer")
        
        finally:
            self.queue.disconnect() 