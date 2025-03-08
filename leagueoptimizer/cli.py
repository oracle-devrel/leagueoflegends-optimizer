"""
Command-line interface for the League Optimizer.

This module provides a command-line interface for the League Optimizer
with subcommands for different functionality.
"""
import argparse
import sys
from typing import List, Optional

from leagueoptimizer.api.live_client import LiveClientConsumer, LiveClientProducer
from leagueoptimizer.config.settings import CONFIG
from leagueoptimizer.utils.logging import app_logger as logger
from leagueoptimizer.visualization.web_app import start_visualizer


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="League of Legends Optimizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Player list command
    player_list_parser = subparsers.add_parser(
        "player-list", help="Get players above masters' elo in all regions"
    )
    
    # Match list command
    match_list_parser = subparsers.add_parser(
        "match-list", help="Get match IDs for players"
    )
    
    # Match download command
    match_download_parser = subparsers.add_parser(
        "match-download", help="Download match data"
    )
    match_download_parser.add_argument(
        "--detail",
        action="store_true",
        help="Download detailed match data",
    )
    
    # Process predictor command
    process_predictor_parser = subparsers.add_parser(
        "process-predictor", help="Process data for prediction"
    )
    process_predictor_parser.add_argument(
        "--live-client",
        action="store_true",
        help="Process data for live client prediction",
    )
    
    # Live client producer command
    live_client_producer_parser = subparsers.add_parser(
        "live-client-producer", help="Start the live client producer"
    )
    live_client_producer_parser.add_argument(
        "--ip",
        type=str,
        default="localhost",
        help="RabbitMQ server IP address",
    )
    live_client_producer_parser.add_argument(
        "--interval",
        type=int,
        default=CONFIG["live_client"]["request_interval"],
        help="Request interval in seconds",
    )
    
    # Live client consumer command
    live_client_consumer_parser = subparsers.add_parser(
        "live-client-consumer", help="Start the live client consumer"
    )
    live_client_consumer_parser.add_argument(
        "--ip",
        type=str,
        default="localhost",
        help="RabbitMQ server IP address",
    )
    live_client_consumer_parser.add_argument(
        "-p", "--path",
        type=str,
        default=CONFIG["model"]["save_path"],
        help="Path to the trained model",
    )
    
    # Visualizer command
    visualizer_parser = subparsers.add_parser(
        "visualizer", help="Start the game data visualizer"
    )
    visualizer_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the visualizer on",
    )
    visualizer_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the visualizer on",
    )
    visualizer_parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode",
    )
    
    # All command
    all_parser = subparsers.add_parser(
        "all", help="Run all commands in sequence"
    )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the command-line interface.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code
    """
    parsed_args = parse_args(args)
    
    if parsed_args.command is None:
        logger.error("No command specified")
        return 1
    
    try:
        if parsed_args.command == "player-list":
            from leagueoptimizer.data.player_list import get_player_list
            get_player_list()
        
        elif parsed_args.command == "match-list":
            from leagueoptimizer.data.match_list import get_match_list
            get_match_list()
        
        elif parsed_args.command == "match-download":
            from leagueoptimizer.data.match_download import download_matches
            download_matches(detailed=parsed_args.detail)
        
        elif parsed_args.command == "process-predictor":
            from leagueoptimizer.data.process_predictor import process_data
            process_data(live_client=parsed_args.live_client)
        
        elif parsed_args.command == "live-client-producer":
            # Update message queue config
            CONFIG["message_queue"]["host"] = parsed_args.ip
            
            # Update live client config
            CONFIG["live_client"]["request_interval"] = parsed_args.interval
            
            # Start producer
            producer = LiveClientProducer()
            producer.start()
        
        elif parsed_args.command == "live-client-consumer":
            # Update message queue config
            CONFIG["message_queue"]["host"] = parsed_args.ip
            
            # Update model config
            CONFIG["model"]["save_path"] = parsed_args.path
            
            # Start consumer
            consumer = LiveClientConsumer()
            consumer.start()
        
        elif parsed_args.command == "visualizer":
            start_visualizer(
                host=parsed_args.host,
                port=parsed_args.port,
                debug=parsed_args.debug,
            )
        
        elif parsed_args.command == "all":
            # Run all commands in sequence
            from leagueoptimizer.data.player_list import get_player_list
            from leagueoptimizer.data.match_list import get_match_list
            from leagueoptimizer.data.match_download import download_matches
            from leagueoptimizer.data.process_predictor import process_data
            
            logger.info("Running all commands in sequence")
            
            logger.info("Getting player list")
            get_player_list()
            
            logger.info("Getting match list")
            get_match_list()
            
            logger.info("Downloading standard match data")
            download_matches(detailed=False)
            
            logger.info("Downloading detailed match data")
            download_matches(detailed=True)
            
            logger.info("Processing data for prediction")
            process_data(live_client=False)
            
            logger.info("Processing data for live client prediction")
            process_data(live_client=True)
            
            logger.info("All commands completed successfully")
        
        else:
            logger.error(f"Unknown command: {parsed_args.command}")
            return 1
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 