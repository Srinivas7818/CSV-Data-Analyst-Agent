
import os
import json

from dotenv import load_dotenv
from groq import Groq

from tools import (
    get_dataset_overview,
    get_column_summary,
    analyze_numeric_column,
    group_by_analysis,
    get_top_values
)


# --------------------------------------------------
# 1. Load Groq API key
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-20b"


# --------------------------------------------------
# 2. Define AI tools
# --------------------------------------------------

tools = [

    {
        "type": "function",
        "function": {
            "name": "get_dataset_overview",
            "description": (
                "Get the total number of rows and columns, "
                "column names, data types and missing values. "
                "Use this for general questions about the dataset "
                "and questions asking how many records or rows exist."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_column_summary",
            "description": (
                "Get statistics and information about a specific "
                "column, including data type, missing values, "
                "unique values and numeric summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "Exact column name from the uploaded CSV."
                    }
                },
                "required": ["column"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "analyze_numeric_column",
            "description": (
                "Perform a numerical calculation on a column. "
                "Use for sum, average, minimum, maximum, median, "
                "count or standard deviation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "Exact numeric column name."
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "sum",
                            "average",
                            "minimum",
                            "maximum",
                            "median",
                            "count",
                            "standard_deviation"
                        ],
                        "description": "Calculation to perform."
                    }
                },
                "required": ["column", "operation"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "group_by_analysis",
            "description": (
                "Group rows using a categorical column and calculate "
                "an aggregate on another column. Useful for department-wise "
                "salary, category-wise sales and similar questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "group_column": {
                        "type": "string",
                        "description": "Column used to create groups."
                    },
                    "value_column": {
                        "type": "string",
                        "description": "Column used for calculation."
                    },
                    "operation": {
                        "type": "string",
                        "enum": [
                            "sum",
                            "average",
                            "minimum",
                            "maximum",
                            "count"
                        ],
                        "description": "Calculation for each group."
                    }
                },
                "required": [
                    "group_column",
                    "value_column",
                    "operation"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_top_values",
            "description": (
                "Find the most frequent values in a column. "
                "Useful for questions about common departments, "
                "categories, names or other repeated values."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "column": {
                        "type": "string",
                        "description": "Exact column name."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results, from 1 to 100."
                    }
                },
                "required": ["column", "limit"]
            }
        }
    }

]


# --------------------------------------------------
# 3. Agent function
# --------------------------------------------------

def ask_agent(question, df):

    available_functions = {
        "get_dataset_overview": get_dataset_overview,
        "get_column_summary": get_column_summary,
        "analyze_numeric_column": analyze_numeric_column,
        "group_by_analysis": group_by_analysis,
        "get_top_values": get_top_values
    }

    # Give the AI the actual uploaded column names and data types.
    dataset_information = {
        "columns": list(df.columns),
        "data_types": {
            str(column): str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "total_rows": len(df)
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a CSV Data Analyst AI Assistant. "
                "Analyze the user's uploaded dataset using Python tools. "
                "The dataset is already loaded. "
                "Use the exact column names provided in the dataset information. "
                "Never invent column names or results. "
                "Choose the most relevant tool for the question. "

                "For row counts and general dataset questions, use "
                "get_dataset_overview. "

                "For numeric calculations, use analyze_numeric_column. "

                "For group-wise calculations, use group_by_analysis. "

                "For column information, use get_column_summary. "

                "For frequently occurring values, use get_top_values. "

                "Do not assume a currency or unit. "
                "Never add currency symbols such as $, ₹, or € "
                "unless the dataset or user explicitly specifies the currency. "
                "Do not assume that salary or sales values are in dollars. "
                "Preserve the numeric values returned by Python accurately. "

                "\n\nDataset information:\n"
                + json.dumps(dataset_information, indent=2)
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # --------------------------------------------------
    # 4. Ask Groq to select a tool
    # --------------------------------------------------

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="required",
        temperature=0
    )

    response_message = response.choices[0].message

    if not response_message.tool_calls:
        return "The AI did not select a Python analysis tool."

    tool_results = {}

    # --------------------------------------------------
    # 5. Execute selected tools
    # --------------------------------------------------

    for tool_call in response_message.tool_calls:

        function_name = tool_call.function.name

        if function_name in tool_results:
            continue

        if function_name not in available_functions:
            tool_results[function_name] = {
                "error": "Tool is not available."
            }
            continue

        try:

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"Agent selected tool: {function_name}"
            )

            print(
                f"Tool arguments: {arguments}"
            )

            result = available_functions[function_name](
                df,
                **arguments
            )

            tool_results[function_name] = {
                "result": result
            }

        except Exception as error:

            tool_results[function_name] = {
                "error": str(error)
            }

    # --------------------------------------------------
    # 6. Generate final response
    # --------------------------------------------------

    final_messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful CSV data analyst. "

                "Answer using only the supplied Python tool results. "
                "Do not invent data or calculations. "

                "Do not assume a currency, measurement unit, "
                "or other information that is not present in the dataset. "

                "Never add $, ₹, €, or any currency symbol unless "
                "the dataset or user explicitly specifies it. "

                "Preserve the exact numerical meaning of Python results. "
                "You may round long decimal values to two decimal places, "
                "but do not change the underlying result. "

                "Use the actual column names from the dataset. "
                "Explain the result clearly and concisely."
            )
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"Python tool results:\n"
                f"{json.dumps(tool_results, indent=2)}"
            )
        }
    ]

    try:

        final_response = client.chat.completions.create(
            model=MODEL,
            messages=final_messages,
            temperature=0
        )

        answer = final_response.choices[0].message.content

        if answer:
            return answer

    except Exception as error:

        print("Final AI response failed:", error)

    # --------------------------------------------------
    # 7. Fallback response
    # --------------------------------------------------

    return (
        "Python analysis completed. Results:\n\n"
        + json.dumps(tool_results, indent=2)
    )
