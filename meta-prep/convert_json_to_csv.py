import json
import csv

def convert_json_to_csv():
    # Read the JSON file
    with open('top-300-meta-tagged-leetcode.json', 'r') as json_file:
        data = json.load(json_file)
    
    # Open CSV file for writing
    with open('top-300-meta-tagged-lc.csv', 'w', newline='', encoding='utf-8') as csv_file:
        # Define headers as specified
        headers = ['Title', 'status', 'frequency', 'tags', 'link']
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        
        # Write header row
        writer.writeheader()
        
        # Process each item in the JSON array
        for item in data:
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
                'frequency': item['frequency'],
                'tags': tags_str,
                'link': link
            }
            
            # Write row to CSV
            writer.writerow(row)
    
    print("CSV file 'top-300-meta-tagged-lc.csv' has been created successfully!")
    print(f"Total records processed: {len(data)}")

if __name__ == "__main__":
    convert_json_to_csv() 