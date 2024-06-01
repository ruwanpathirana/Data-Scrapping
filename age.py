import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define the main Wikipedia URL
main_url = 'https://en.wikipedia.org/wiki/16th_Parliament_of_Sri_Lanka'     
table_classes = ["plainrowheaders"]

# Fetch the main page
response = requests.get(main_url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch the main page. Status code: {response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')

# # Print all table classes to debug
# tables = soup.find_all('table')
# print("Available table classes:")
# for i, table in enumerate(tables):
#     print(f"Table {i}: {table.get('class')}")

# Find the table containing the list of members
table = soup.find('table', {'class': table_classes})

# Check if the table was found
if table is None:
    raise Exception("Failed to find the table. Please check the class name and structure of the Wikipedia page.")

# df=pd.read_html(str(table))
# # convert list to dataframe
# df=pd.DataFrame(df[0])
# print(df.head())

# Extract the links to individual member pages
members = []
for row in table.find_all('tr')[1:]:  # Skipping the header row
    cols = row.find_all('td')
    if len(cols) > 0:
        name = cols[0].text.strip()

        party_cell = cols[10]
        party_tag = party_cell.find('a', href=True)  # Find the anchor tag within the party cell
        party = party_tag.text.strip() if party_tag else 'Unknown'
        # Print the content of the party cell for debugging
        #rint("Party Cell Content:", party_cell)
        
        # Print the content of the party tag for debugging
        #print("Party Tag Content:", party_tag)

        link = cols[0].find('a', href=True)
        if link:
            member_url = 'https://en.wikipedia.org' + link['href']
        else:
            member_url = None
        members.append((name, member_url, party))


# Function to extract birthdate from individual member page
def get_member_birthdate(url):
    if url is None:
        return 'unknown'
    
    response = requests.get(url)
    if response.status_code != 200:
        return 'unknown'
    
    member_soup = BeautifulSoup(response.content, 'html.parser')
    
    # Check for the birthdate in the infobox
    birthdate = 'unknown'
    infobox = member_soup.find('table', {'class': 'infobox vcard'})
    if infobox:
        bday_span = infobox.find('span', {'class': 'bday'})
        if bday_span:
            birthdate = bday_span.text.strip()  # Extract the text of the span
            birthdate = birthdate.split('(')[0].strip()
    
    return birthdate

# Fetch birthdate for each member
member_data = []
for name, url, party in members:
    birthdate = get_member_birthdate(url)
    print(f"Name: {name}, Birthdate: {birthdate}, Party:{party}")
    member_data.append((name, birthdate, party))

# Save the data to a CSV file
df = pd.DataFrame(member_data, columns=['Name', 'Birthdate', 'Party'])
df.to_csv('parliament_members_birthdates_new.csv', index=False)