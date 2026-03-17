import asyncio
import requests
from server import predict_oem_tyre_size_from_query

async def test():
    print("--- Testing API-based errors ---")
    print("Testing invalid brand (NonExistentBrand)...")
    res = await predict_oem_tyre_size_from_query("NonExistentBrand", "Corolla", 2020)
    print(f"Result: {res}\n")

    print("Testing invalid model (NonExistentModel)...")
    res = await predict_oem_tyre_size_from_query("Toyota", "NonExistentModel", 2020)
    print(f"Result: {res}\n")

    print("--- Testing input validation errors ---")
    print("Testing empty brand...")
    res = await predict_oem_tyre_size_from_query("", "Corolla", 2020)
    print(f"Result: {res}\n")

    print("Testing empty model...")
    res = await predict_oem_tyre_size_from_query("Toyota", "", 2020)
    print(f"Result: {res}\n")

    print("--- Testing success case ---")
    print("Testing Toyota Corolla 2020...")
    res = await predict_oem_tyre_size_from_query("Toyota", "Corolla", 2020)
    print(f"Result: {res}\n")

if __name__ == "__main__":
    asyncio.run(test())
