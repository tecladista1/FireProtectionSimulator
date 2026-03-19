import asyncio
from bacpypes3.ipv4.app import Application
from bacpypes3.object import BinaryValueObject
from bacpypes3.primitivedata import ObjectIdentifier

async def main():
    print("Building app...")
    # Application is defined in bacpypes3.ipv4.app
    app = Application.from_local_address("0.0.0.0")
    print("App built. Adding object...")
    
    obj = BinaryValueObject(
        objectIdentifier='binaryValue:1',
        objectName='Test',
        presentValue='inactive'
    )
    app.add_object(obj)
    print("Object added successfully!")
    
if __name__ == "__main__":
    asyncio.run(main())
