"""
Web application for visualizing League of Legends game data.

This module provides a Flask web application that serves a Three.js
visualization of the game data from the Live Client API.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO

from leagueoptimizer.api.live_client import LiveClientAPI, LiveClientError
from leagueoptimizer.config.settings import CONFIG
from leagueoptimizer.utils.logging import app_logger as logger
from leagueoptimizer.utils.message_queue import get_message_queue


class GameDataVisualizer:
    """Visualizer for League of Legends game data."""
    
    def __init__(self, static_folder: Optional[str] = None):
        """
        Initialize the game data visualizer.
        
        Args:
            static_folder: The folder for static files
        """
        # Create Flask app
        self.app = Flask(
            __name__,
            static_folder=static_folder or str(Path(__file__).parent / "static"),
            template_folder=str(Path(__file__).parent / "templates"),
        )
        
        # Configure app
        self.app.config["SECRET_KEY"] = "league-optimizer"
        
        # Create SocketIO instance
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Create Live Client API instance
        self.api = LiveClientAPI()
        
        # Create message queue consumer
        self.queue = get_message_queue()
        
        # Register routes
        self._register_routes()
        
        # Register SocketIO events
        self._register_socketio_events()
        
        # Create templates and static files
        self._create_templates()
        self._create_static_files()
    
    def _register_routes(self) -> None:
        """Register Flask routes."""
        
        @self.app.route("/")
        def index():
            """Render the index page."""
            return render_template("index.html")
        
        @self.app.route("/api/game-data")
        def game_data():
            """Get game data from the Live Client API."""
            try:
                data = self.api.get_all_game_data()
                return jsonify(data)
            except LiveClientError as e:
                return jsonify({"error": str(e)}), 404
        
        @self.app.route("/api/prediction")
        def prediction():
            """Get prediction for the current game state."""
            try:
                # Get game data
                game_data = self.api.get_all_game_data()
                
                # Extract features for prediction
                features = self.api.extract_prediction_features(game_data)
                
                # Convert to DataFrame for prediction
                import pandas as pd
                sample_df = pd.DataFrame([features])
                
                # Load model and make prediction
                from autogluon.tabular import TabularPredictor
                predictor = TabularPredictor.load(CONFIG["model"]["save_path"])
                prediction = predictor.predict(sample_df)
                pred_probs = predictor.predict_proba(sample_df)
                
                # Format prediction
                expected_result = prediction.get(0)
                win_prob = float(pred_probs.iloc[0][1]) if expected_result == 1 else float(pred_probs.iloc[0][0])
                
                return jsonify({
                    "prediction": "WIN" if expected_result == 1 else "LOSS",
                    "probability": win_prob * 100,
                    "win_probability": float(pred_probs.iloc[0][1]) * 100,
                    "loss_probability": float(pred_probs.iloc[0][0]) * 100,
                })
            
            except LiveClientError as e:
                return jsonify({"error": str(e)}), 404
            except Exception as e:
                logger.error(f"Error making prediction: {e}")
                return jsonify({"error": str(e)}), 500
    
    def _register_socketio_events(self) -> None:
        """Register SocketIO events."""
        
        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection."""
            logger.info("Client connected")
        
        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection."""
            logger.info("Client disconnected")
    
    def _create_templates(self) -> None:
        """Create template files."""
        # Create templates directory if it doesn't exist
        templates_dir = Path(self.app.template_folder)
        templates_dir.mkdir(exist_ok=True)
        
        # Create index.html
        index_html = templates_dir / "index.html"
        if not index_html.exists():
            with open(index_html, "w") as f:
                f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>League of Legends Optimizer</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>League of Legends Optimizer</h1>
        </header>
        
        <div class="dashboard">
            <div class="visualization">
                <div id="3d-visualization"></div>
            </div>
            
            <div class="stats">
                <div class="prediction">
                    <h2>Win Prediction</h2>
                    <div class="prediction-value">
                        <span id="prediction-text">Waiting for game data...</span>
                    </div>
                    <div class="prediction-bar">
                        <div id="win-bar" class="win-bar"></div>
                        <div id="loss-bar" class="loss-bar"></div>
                    </div>
                </div>
                
                <div class="player-stats">
                    <h2>Player Stats</h2>
                    <div id="player-stats-container"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/visualization.js') }}"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>""")
    
    def _create_static_files(self) -> None:
        """Create static files."""
        # Create static directory if it doesn't exist
        static_dir = Path(self.app.static_folder)
        static_dir.mkdir(exist_ok=True)
        
        # Create CSS directory
        css_dir = static_dir / "css"
        css_dir.mkdir(exist_ok=True)
        
        # Create JS directory
        js_dir = static_dir / "js"
        js_dir.mkdir(exist_ok=True)
        
        # Create style.css
        style_css = css_dir / "style.css"
        if not style_css.exists():
            with open(style_css, "w") as f:
                f.write("""* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background-color: #0a0a0a;
    color: #ffffff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
}

header h1 {
    color: #d0a85c;
    font-size: 2.5rem;
}

.dashboard {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
}

.visualization {
    flex: 1;
    min-width: 600px;
    height: 500px;
    background-color: #1a1a1a;
    border-radius: 10px;
    overflow: hidden;
}

#3d-visualization {
    width: 100%;
    height: 100%;
}

.stats {
    flex: 1;
    min-width: 300px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.prediction, .player-stats {
    background-color: #1a1a1a;
    border-radius: 10px;
    padding: 20px;
}

.prediction h2, .player-stats h2 {
    color: #d0a85c;
    margin-bottom: 15px;
}

.prediction-value {
    font-size: 2rem;
    text-align: center;
    margin-bottom: 15px;
}

.prediction-bar {
    height: 30px;
    background-color: #333;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
}

.win-bar {
    height: 100%;
    background-color: #4caf50;
    width: 50%;
    position: absolute;
    left: 0;
    transition: width 0.5s ease;
}

.loss-bar {
    height: 100%;
    background-color: #f44336;
    width: 50%;
    position: absolute;
    right: 0;
    transition: width 0.5s ease;
}

.player-stats-item {
    margin-bottom: 10px;
    padding: 10px;
    background-color: #2a2a2a;
    border-radius: 5px;
}

.player-stats-item h3 {
    color: #d0a85c;
    margin-bottom: 5px;
}

.player-stats-item p {
    margin: 5px 0;
}

@media (max-width: 768px) {
    .dashboard {
        flex-direction: column;
    }
    
    .visualization {
        min-width: 100%;
        height: 300px;
    }
}""")
        
        # Create app.js
        app_js = js_dir / "app.js"
        if not app_js.exists():
            with open(app_js, "w") as f:
                f.write("""// Connect to Socket.IO server
const socket = io();

// Game data polling interval (in milliseconds)
const POLLING_INTERVAL = 5000;

// Store game data
let gameData = null;

// Function to fetch game data from the API
async function fetchGameData() {
    try {
        const response = await fetch('/api/game-data');
        if (!response.ok) {
            throw new Error('Game data not available');
        }
        
        gameData = await response.json();
        updateVisualization(gameData);
        updatePlayerStats(gameData);
        
        // Fetch prediction
        fetchPrediction();
        
        return gameData;
    } catch (error) {
        console.error('Error fetching game data:', error);
        document.getElementById('prediction-text').textContent = 'Waiting for game data...';
        return null;
    }
}

// Function to fetch prediction from the API
async function fetchPrediction() {
    try {
        const response = await fetch('/api/prediction');
        if (!response.ok) {
            throw new Error('Prediction not available');
        }
        
        const prediction = await response.json();
        updatePrediction(prediction);
        
        return prediction;
    } catch (error) {
        console.error('Error fetching prediction:', error);
        return null;
    }
}

// Function to update prediction display
function updatePrediction(prediction) {
    const predictionText = document.getElementById('prediction-text');
    const winBar = document.getElementById('win-bar');
    const lossBar = document.getElementById('loss-bar');
    
    if (prediction.prediction === 'WIN') {
        predictionText.textContent = `WIN (${prediction.win_probability.toFixed(2)}%)`;
        predictionText.style.color = '#4caf50';
    } else {
        predictionText.textContent = `LOSS (${prediction.loss_probability.toFixed(2)}%)`;
        predictionText.style.color = '#f44336';
    }
    
    winBar.style.width = `${prediction.win_probability}%`;
    lossBar.style.width = `${prediction.loss_probability}%`;
}

// Function to update player stats display
function updatePlayerStats(gameData) {
    const playerStatsContainer = document.getElementById('player-stats-container');
    playerStatsContainer.innerHTML = '';
    
    if (!gameData || !gameData.activePlayer || !gameData.activePlayer.championStats) {
        playerStatsContainer.innerHTML = '<p>No player data available</p>';
        return;
    }
    
    const stats = gameData.activePlayer.championStats;
    
    const statsDiv = document.createElement('div');
    statsDiv.className = 'player-stats-item';
    
    statsDiv.innerHTML = `
        <h3>${gameData.activePlayer.summonerName || 'Active Player'}</h3>
        <p>Health: ${stats.currentHealth.toFixed(0)}/${stats.maxHealth.toFixed(0)}</p>
        <p>Attack Damage: ${stats.attackDamage.toFixed(1)}</p>
        <p>Ability Power: ${stats.abilityPower.toFixed(1)}</p>
        <p>Armor: ${stats.armor.toFixed(1)}</p>
        <p>Magic Resist: ${stats.magicResist.toFixed(1)}</p>
        <p>Move Speed: ${stats.moveSpeed.toFixed(1)}</p>
        <p>Attack Speed: ${stats.attackSpeed.toFixed(2)}</p>
    `;
    
    playerStatsContainer.appendChild(statsDiv);
    
    // Add other players
    if (gameData.allPlayers) {
        gameData.allPlayers.forEach(player => {
            if (player.summonerName !== gameData.activePlayer.summonerName) {
                const playerDiv = document.createElement('div');
                playerDiv.className = 'player-stats-item';
                
                const team = player.team === 'ORDER' ? 'Blue' : 'Red';
                
                playerDiv.innerHTML = `
                    <h3>${player.summonerName} (${team})</h3>
                    <p>Champion: ${player.championName}</p>
                    <p>Level: ${player.level}</p>
                    <p>Position: ${player.position || 'Unknown'}</p>
                `;
                
                playerStatsContainer.appendChild(playerDiv);
            }
        });
    }
}

// Start polling for game data
setInterval(fetchGameData, POLLING_INTERVAL);

// Initial fetch
fetchGameData();""")
        
        # Create visualization.js
        visualization_js = js_dir / "visualization.js"
        if not visualization_js.exists():
            with open(visualization_js, "w") as f:
                f.write("""// Three.js visualization
let scene, camera, renderer;
let championMeshes = {};
let statsLabels = {};

// Initialize the 3D scene
function initVisualization() {
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    // Create camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 10, 20);
    camera.lookAt(0, 0, 0);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    
    // Add renderer to the DOM
    const container = document.getElementById('3d-visualization');
    container.appendChild(renderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Add ground plane
    const groundGeometry = new THREE.PlaneGeometry(50, 50);
    const groundMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x333333,
        side: THREE.DoubleSide
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = Math.PI / 2;
    ground.position.y = -1;
    scene.add(ground);
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation loop
    animate();
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

// Create a champion mesh
function createChampionMesh(team, position = { x: 0, y: 0, z: 0 }) {
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const material = new THREE.MeshStandardMaterial({ 
        color: team === 'ORDER' ? 0x0066ff : 0xff3333,
        emissive: team === 'ORDER' ? 0x003399 : 0x990000,
        emissiveIntensity: 0.3,
        roughness: 0.7,
        metalness: 0.3
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(position.x, position.y, position.z);
    scene.add(mesh);
    
    return mesh;
}

// Create a text label for stats
function createStatsLabel(text, position) {
    // This is a placeholder since Three.js doesn't have built-in text support
    // In a real implementation, you would use a library like troika-three-text
    // or create a sprite with canvas-generated text
    
    const geometry = new THREE.BoxGeometry(0.1, 0.1, 0.1);
    const material = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const label = new THREE.Mesh(geometry, material);
    label.position.set(position.x, position.y + 2, position.z);
    label.visible = false; // Hide the placeholder
    scene.add(label);
    
    // In a real implementation, you would attach the text to this object
    label.userData.text = text;
    
    return label;
}

// Update the visualization with game data
function updateVisualization(gameData) {
    if (!scene) {
        initVisualization();
    }
    
    if (!gameData || !gameData.allPlayers) {
        return;
    }
    
    // Calculate positions for champions
    const blueTeamPositions = [
        { x: -8, y: 0, z: -8 },
        { x: -4, y: 0, z: -8 },
        { x: 0, y: 0, z: -8 },
        { x: 4, y: 0, z: -8 },
        { x: 8, y: 0, z: -8 }
    ];
    
    const redTeamPositions = [
        { x: -8, y: 0, z: 8 },
        { x: -4, y: 0, z: 8 },
        { x: 0, y: 0, z: 8 },
        { x: 4, y: 0, z: 8 },
        { x: 8, y: 0, z: 8 }
    ];
    
    let blueIndex = 0;
    let redIndex = 0;
    
    // Update or create champion meshes
    gameData.allPlayers.forEach(player => {
        const team = player.team;
        const summonerName = player.summonerName;
        
        // Determine position based on team
        let position;
        if (team === 'ORDER') {
            position = blueTeamPositions[blueIndex];
            blueIndex = (blueIndex + 1) % blueTeamPositions.length;
        } else {
            position = redTeamPositions[redIndex];
            redIndex = (redIndex + 1) % redTeamPositions.length;
        }
        
        // Create or update champion mesh
        if (!championMeshes[summonerName]) {
            championMeshes[summonerName] = createChampionMesh(team, position);
            statsLabels[summonerName] = createStatsLabel(`${player.championName} (${player.level})`, position);
        } else {
            // Update position
            championMeshes[summonerName].position.set(position.x, position.y, position.z);
            statsLabels[summonerName].position.set(position.x, position.y + 2, position.z);
            
            // Update label text
            statsLabels[summonerName].userData.text = `${player.championName} (${player.level})`;
        }
        
        // Update champion size based on level
        const scale = 0.5 + (player.level * 0.05);
        championMeshes[summonerName].scale.set(scale, scale, scale);
        
        // Update champion color based on health
        if (player.isDead) {
            championMeshes[summonerName].material.color.setHex(0x666666);
            championMeshes[summonerName].material.emissive.setHex(0x333333);
        } else {
            championMeshes[summonerName].material.color.setHex(team === 'ORDER' ? 0x0066ff : 0xff3333);
            championMeshes[summonerName].material.emissive.setHex(team === 'ORDER' ? 0x003399 : 0x990000);
        }
    });
}

// Initialize visualization when the page loads
window.addEventListener('load', initVisualization);""")
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
        """
        Run the Flask application.
        
        Args:
            host: The host to run on
            port: The port to run on
            debug: Whether to run in debug mode
        """
        self.socketio.run(self.app, host=host, port=port, debug=debug)


def start_visualizer(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Start the game data visualizer.
    
    Args:
        host: The host to run on
        port: The port to run on
        debug: Whether to run in debug mode
    """
    visualizer = GameDataVisualizer()
    visualizer.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    start_visualizer(debug=True) 