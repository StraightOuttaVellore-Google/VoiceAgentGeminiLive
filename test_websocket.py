#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/test_client"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "config",
                "config": {
                    "systemPrompt": "Test prompt",
                    "voice": "Puck",
                    "allowInterruptions": False,
                    "mode": "wellness"
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("Test message sent")
            
            # Give the backend a moment to process the config
            await asyncio.sleep(1)
            
            # Wait for responses with longer timeout
            try:
                # Wait for multiple responses with longer timeout
                response_count = 0
                max_responses = 5  # Increased from 3
                timeout_per_response = 8.0  # Increased from 5.0
                
                while response_count < max_responses:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=timeout_per_response)
                        response_count += 1
                        print(f"Received response {response_count}: {response}")
                        
                        # Parse response to check if we got the expected messages
                        try:
                            response_data = json.loads(response)
                            if response_data.get("type") == "status":
                                status = response_data.get('status')
                                text = response_data.get('text', '')
                                print(f"Status: {status} - {text}")
                                
                                # If we get 'connected' status, we can consider the test successful
                                if status == "connected":
                                    print("✅ Successfully connected to AI service!")
                                    break
                            elif response_data.get("type") == "error":
                                print(f"❌ Error: {response_data.get('text', '')}")
                                break
                        except json.JSONDecodeError:
                            print(f"Non-JSON response: {response}")
                            
                    except asyncio.TimeoutError:
                        print(f"Timeout waiting for response {response_count + 1}")
                        break
                        
            except Exception as e:
                print(f"Error receiving response: {e}")
            
    except Exception as e:
        print(f"WebSocket connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())
