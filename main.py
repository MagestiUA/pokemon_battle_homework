import json
import aiohttp
import asyncio
import random

async def fetch_json(session, url):
	async with session.get(url) as response:
		return await response.json()

def save_to_json(data_dict):
	try:
		with open('detailed_data.json', "w", encoding="utf-8") as file:
			json.dump(data_dict, file, indent=4, ensure_ascii=False, sort_keys=True)
	except Exception as e:
		print(f"Помилка збереження detailed_data.json: {e}")


async def get_pokemon_data():
	base_url = "https://pokeapi.co/api/v2/pokemon/"
	async with aiohttp.ClientSession() as session:
		data = await fetch_json(session, base_url)

		pokemon_base_data = {item["name"]: item["url"] for item in data["results"]}
		print(f"Отримано {len(pokemon_base_data)} покемонів:")
		print(pokemon_base_data)

		detailed_data = {}
		for name, url in pokemon_base_data.items():
			print(f"Завантаження даних для {name}...")
			pokemon_data = await fetch_json(session, url)
			detailed_data[name] = pokemon_data
		print(f"Детальна інформація про {len(detailed_data)} покемонів отримана.")
	save_to_json(detailed_data)
	first_pokemon = random.choice(list(pokemon_base_data.keys()))
	second_pokemon = random.choice(list(pokemon_base_data.keys()))
	return first_pokemon, second_pokemon


async def fetch_pokemon_data(session, name):
	url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
	async with session.get(url) as response:
		if response.status == 200:
			return await response.json()
		else:
			print(f"Помилка: Не вдалося отримати дані для {name}")
			return None


def calculate_damage(attack, defense):
	return max(1, (attack + random.randint(-5, 5)) - defense)


async def battle(pokemon1, pokemon2):
	async with aiohttp.ClientSession() as session:
		p1_data = await fetch_pokemon_data(session, pokemon1)
		p2_data = await fetch_pokemon_data(session, pokemon2)
		
		if not p1_data or not p2_data:
			print("Бій не може бути проведений через помилку завантаження даних.")
			return

		p1_attack = p1_data["stats"][1]["base_stat"]
		p1_defense = p1_data["stats"][2]["base_stat"]
		p2_attack = p2_data["stats"][1]["base_stat"]
		p2_defense = p2_data["stats"][2]["base_stat"]
		
		p1_hp = p1_data["stats"][0]["base_stat"]
		p2_hp = p2_data["stats"][0]["base_stat"]
		
		print(f"Початок бою: {pokemon1} (HP: {p1_hp}) vs {pokemon2} (HP: {p2_hp})")
		
		turn = 0
		while p1_hp > 0 and p2_hp > 0:
			turn += 1
			print(f"\nХід {turn}:")
			damage = calculate_damage(p1_attack, p2_defense)
			p2_hp -= damage
			print(f"{pokemon1} завдав {damage} шкоди {pokemon2}. HP {pokemon2}: {max(0, p2_hp)}")
			
			if p2_hp <= 0:
				print(f"{pokemon2} програв!")
				break
			
			damage = calculate_damage(p2_attack, p1_defense)
			p1_hp -= damage
			print(f"{pokemon2} завдав {damage} шкоди {pokemon1}. HP {pokemon1}: {max(0, p1_hp)}")
			
			if p1_hp <= 0:
				print(f"{pokemon1} програв!")
		
		print("\nБій завершено.")


async def main():
	first_pokemon, second_pokemon = await get_pokemon_data()
	print(f"Випадкові покемони: {first_pokemon} vs {second_pokemon}")
	await battle(first_pokemon, second_pokemon)

asyncio.run(main())