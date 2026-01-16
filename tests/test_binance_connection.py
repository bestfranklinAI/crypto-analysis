import asyncio
import websockets
import json

async def test_connection():
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    
    print("Connecting to Binance WebSocket...")
    
    async with websockets.connect(url) as websocket:
        print("Connected. Listening for messages...")
        
        for i in range(5):
            message = await websocket.recv()
            trade = json.loads(message)
            print(f"{i+1}. {trade['s']}: ${trade['p']} x {trade['q']}")
        print("Received 5 messages. Closing connection.")
        
if __name__ == "__main__":
    asyncio.run(test_connection())
    