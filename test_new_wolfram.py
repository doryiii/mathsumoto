import asyncio
from wolfram import get_wolfram

async def main():
    print("Querying '2+2'...")
    text, img = await get_wolfram("2+2")
    print(f"Result text: {text}")
    print(f"Image type: {type(img)}")

    print("\nQuerying 'plot x^2'...")
    text, img = await get_wolfram("plot x^2")
    print(f"Result text: {text}")
    print(f"Image type: {type(img)}")
    
    print("\nQuerying 'what is the airspeed velocity of an unladen swallow'...")
    text, img = await get_wolfram("what is the airspeed velocity of an unladen swallow")
    print(f"Result text: {text}")

if __name__ == "__main__":
    asyncio.run(main())

