import json
import csv

def convert_json_to_csv():
    # Read the JSON file
    with open('airbnb-alltime-lc.json', 'r') as json_file:
        data = json.load(json_file)
    
    # Open CSV file for writing
    with open('airbnb-alltime-lc.csv', 'w', newline='', encoding='utf-8') as csv_file:
        # Define headers as specified
        headers = ['Title', 'status', 'difficulty', 'frequency', 'tags', 'link']
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        
        # Write header row
        writer.writeheader()
        
        # Keep track of seen IDs to ensure uniqueness
        seen_ids = set()
        unique_count = 0
        
        # Process each item in the JSON array
        for item in data:
            # Check if this item has an ID and if we've seen it before
            if 'id' in item:
                item_id = item['id']
                if item_id in seen_ids:
                    # Skip this duplicate entry
                    continue
                # Mark this ID as seen
                seen_ids.add(item_id)
            # Extract tags from topicTags array
            tags = []
            if 'topicTags' in item and item['topicTags']:
                tags = [tag['name'] for tag in item['topicTags']]
            tags_str = '; '.join(tags)  # Join with semicolon as delimiter
            
            # Construct the link using titleSlug
            link = f"https://leetcode.com/problems/{item['titleSlug']}/"
            
            # Create row data
            row = {
                'Title': item['title'],
                'status': item['status'],
                'difficulty': item['difficulty'],
                'frequency': item['frequency'],
                'tags': tags_str,
                'link': link
            }
            
            # Write row to CSV
            writer.writerow(row)
            unique_count += 1
    
    print("CSV file 'airbnb-alltime-lc.csv' has been created successfully!")
    print(f"Total records in JSON: {len(data)}")
    print(f"Unique records processed: {unique_count}")
    print(f"Duplicate records skipped: {len(data) - unique_count}")

if __name__ == "__main__":
    convert_json_to_csv() 