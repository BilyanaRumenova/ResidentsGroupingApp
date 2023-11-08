import csv
import re
from io import StringIO

from fastapi import HTTPException
from starlette import status
from translate import Translator


def process_data(data) -> str:
    try:
        people_addresses = handle_input_data(data)
        processed_addresses = process_addresses(people_addresses)
        sorted_data = sorted(processed_addresses.items(), key=lambda x: x[1])
        output = "\n".join(", ".join(names) for _, names in sorted_data)
        return output

    except (ValueError, IndexError, Exception) as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


def handle_input_data(data):
    people_addresses = {}
    try:
        if isinstance(data, str):
            lines = data.splitlines()
            for line in lines:
                if line.strip():
                    name, address = line.split(',', 1)
                    cleaned_address = clean_address_string(address)
                    people_addresses[name] = cleaned_address
            print(people_addresses)
        else:
            contents = data.decode('utf-8')
            reader = csv.DictReader(StringIO(contents))
            for row in reader:
                name = row.get('Name')
                address = row.get('Address')
                cleaned_address = clean_address_string(address)
                people_addresses[name] = cleaned_address

        return people_addresses

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))

def process_addresses(people_addresses: dict) -> dict:
    similar_addresses = {}
    try:
        unmatched_people = set(people_addresses.keys())
        for person1, address1 in people_addresses.items():
            tokenized_address_1 = tokenize_address(address1)
            similar_to_current = [person1]

            for person2, address2 in people_addresses.items():
                if person1 != person2 and person2 not in similar_to_current:
                    tokenized_address_2 = tokenize_address(address2)
                    similarity = jaccard_similarity(tokenized_address_1, tokenized_address_2)
                    if similarity > 0.5:
                        similar_to_current.append(person2)
                        unmatched_people.discard(person2)

            similar_addresses[tuple(sorted(similar_to_current))] = sorted(similar_to_current)

        for person in unmatched_people:
            similar_addresses[(person,)] = [person]

        return similar_addresses

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


def clean_address_string(address: str) -> str:
    cleaned_address = address.replace('”', '').replace('“', '').replace('"', '').replace("'", '').strip()
    if contains_cyrillic(cleaned_address):
        cleaned_address = translate_address(cleaned_address)
    return cleaned_address.lower()

def tokenize_address(address: str) -> set:
    # Tokenizes the address by splitting it into words and removing punctuation
    return set(address.replace(",", "")
               .replace(".", "")
               # .replace(", ", "")
               # .replace(". ", "")
               .split())

def jaccard_similarity(set1, set2) -> float:
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


def translate_address(address: str, source_language='bg', dest_language='en') -> str:
    translator = Translator(from_lang=source_language, to_lang=dest_language)
    translation = translator.translate(address)
    return translation


def contains_cyrillic(address: str) -> bool:
    return bool(re.search('[\u0400-\u04FF]', address))
