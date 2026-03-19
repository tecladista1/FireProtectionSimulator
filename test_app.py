import asyncio
import BAC0

async def main():
    app = BAC0.lite()
    print("this_application type:", type(app.this_application))
    print("this_application dir:", dir(app.this_application))
    app.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
