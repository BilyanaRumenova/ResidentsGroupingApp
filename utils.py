import csv
import re
from io import StringIO

from fastapi import HTTPException
from starlette import status
from translate import Translator


def process_data(data) -> str:
    """Responsible for processing input data to generate the required output format. It takes in input data
    in a generic format (could be CSV or plain text) and transforms it into a formatted string containing
    processed information."""
    try:
        people_addresses = handle_input_data(data)
        processed_addresses = process_addresses(people_addresses)
        sorted_data = sorted(processed_addresses.items(), key=lambda x: x[1])
        output = "\n".join(", ".join(names) for _, names in sorted_data)
        return output

    except (ValueError, IndexError, Exception) as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


def handle_input_data(data):
    """Responsible for handling the input data and preparing it for further processing. It adapts to two
    types of input formats (plain text or CSV) and generates a dictionary (people_addresses) containing names as
    keys and cleaned addresses as values."""
    people_addresses = {}
    try:
        if isinstance(data, str):
            lines = data.splitlines()
            for line in lines:
                if line.strip():
                    name, address = line.split(',', 1)
                    cleaned_address = clean_address_string(address)
                    people_addresses[name] = cleaned_address
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
    """Responsible for analyzing and grouping similar addresses or people based on the similarity of their addresses.
    It takes a dictionary (people_addresses) with names as keys and their respective tokenized addresses as
    values and performs a similarity comparison among the addresses."""
    similar_addresses = {}
    try:
        SIMILARITY_THRESHOLD = 0.5
        unmatched_people = list(people_addresses.keys())
        while unmatched_people:
            current_person = unmatched_people.pop(0)
            similar_to_current = [current_person]
            tokenized_address_1 = tokenize_address(people_addresses[current_person])

            for other_person in unmatched_people[:]:
                tokenized_address_2 = tokenize_address(people_addresses[other_person])
                similarity = jaccard_similarity(tokenized_address_1, tokenized_address_2)
                if similarity > SIMILARITY_THRESHOLD:
                    similar_to_current.append(other_person)
                    unmatched_people.remove(other_person)

            similar_to_current.sort()
            similar_addresses[tuple(similar_to_current)] = similar_to_current

        return similar_addresses

    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))


def clean_address_string(address: str) -> str:
    """Responsible for cleaning the provided address string removing different types of quotation symbols.
    This is needed in order to increase the similarity value when addresses are passed to jaccard_similarity function"""
    cleaned_address = (address.replace('”', '')
                       .replace('“', '')
                       .replace('"', '')
                       .replace("'", '').strip())
    if contains_cyrillic(cleaned_address):
        cleaned_address = translate_address(cleaned_address)
    return cleaned_address.lower()


def tokenize_address(address: str) -> set:
    """Tokenizes the address by splitting it into words and removing punctuation"""
    return set(address.replace(",", "")
               .replace(".", "")
               .split())


def jaccard_similarity(set1, set2) -> float:
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


def translate_address(address: str, source_language='bg', dest_language='en') -> str:
    """Translates the provided address written in Bulgarian to English"""
    translator = Translator(from_lang=source_language, to_lang=dest_language)
    translation = translator.translate(address)
    return translation


def contains_cyrillic(address: str) -> bool:
    """Checks for cyrillic symbols in the provided address"""
    return bool(re.search('[\u0400-\u04FF]', address))