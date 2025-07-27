# webERP AI Agent

This small Python application is a proof of concept AI agent for [webERP](https://weberp.org/) using [Flask](https://flask.palletsprojects.com/en/stable/). It works with [OpenAI]( https://openai.com/). You will need an account to generate an API key and some funds on account. 

The interface presents a text area where the user can type a question (eg: what is the value of the items in stock). This is sent to the AI which will return the relevant query it thinks is the proper one to give the answer. The returned query is displayed on the screen along with the resulting dataset after it is executed. The application is just one call to the AI and does not chain results or provide for detailed querying on returned results.

![the UI](/images/weberai_mainscreen.png)

The LLM is aware of webERP and its database schema. Regardless, as part of the prompt being sent a complete schema in JSON format is sent along as part of the *system* role message. This schema is generated based on the target database, saved to disk and refreshed every number of days as defined by the configuration item *definition_keep_alive_days*. The reason for this is to allow the AI to be aware of any custom developed functionality (through associated tables). An improvement could be to have a more proper dictionary with better description of the tables and fields.

The returned query is executed against the target database and the resulting dataset displayed in a table. 

## Sample Questions
- *which customer spent the most this year to date*
- *which are the top 5 spending customers last year. show the list in descending order by spend* 
- *what is the value of the items in stock*
- *list the open purchase orders, showing the supplier and value*
- *list the open purchase orders, showing the supplier and value and the order date. sort by oldest on top*
