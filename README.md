# ads_scanner
> help you locate new ads and send them directly to a telegram robot

## how to use
### "items_urls_to_scan.txt" file
* This file lists each URL at which you want to perform the scan on a separate line (To undo a line simply add ### at the end of the line)
*  At the end of the line, put in parentheses the number of pages you want to scan 
*  For example https://*******/products/computers-and-accessories?category=6&item=34&price=1000-2000 (5)  
*  The script will crawl the link to page 5 (inclusive) in the search results
### "near_city.txt" file
* Add to this file the names of the cities closest to you
* Each city in a separate line
* Upcoming cities will appear on the telegram with the V mark
### "TELEGRAM_USERS" variable
* important! Do not delete the last comma (it is consumed in case there is only one entry in the list
* Add the usernames to which you want to send the messages 
  #### notes
    * Robots cannot start a conversation with users, the user has to start the conversation and then the robot can send messages to it
    * The robot can send messages to channels, but you must add the robot as a channel manager
### "api_id" "api_hash" variables
You can find them here https://my.telegram.org/auth?to=apps
###  "bot_token" variable
Here you will find a good explanation https://www.siteguarding.com/en/how-to-get-telegram-bot-api-token
### "scrapingbee_token" variable
* go to https://www.scrapingbee.com/ 
* create free acount
* copy your API key and paste it here
## Run the script
