# Smart Home Agent

A Smart Home Agent using OpenAI API can recognize a user voice and instructions and control the devices of SwitchBot in the user home.

## Prerequisites

- To chat with verbally, a mic and speaker are needed.
- To use OpenAI API, an account is needed.
  - Before using OpenAI API, you need credits on the [Billing settings page](https://platform.openai.com/account/billing/overview).
- To call SwitchBot API, an account and TOKEN, API_KEY are needed.
  - <https://github.com/OpenWonderLabs/SwitchBotAPI#getting-started>
- Environment
  - Python: 3.10 and 3.11 are tested.
  - OS: Ubuntu 22.04 (WSL)

## Get started

1. Set parameters

    Create the file `.env` in the repository root and its content is below. Replace the parameters with yours.

    ```txt
    SWITCHBOT_TOKEN={YOUR_TOKEN}
    SWITCHBOT_SECRET_KEY={YOUR_SECRET_KEY}
    ORGANIZATION_ID={YOUR_ORGANIZATION_ID}
    API_KEY={YOUR_API_KEY}
    ```

1. Create a virtual environment

    ```sh
    python -m venv .venv
    ```

1. Activate the virtual environment

    ```sh
    source .venv/bin/activate
    ```

    When deactivate, use `deactivate` command.

1. Install the dependency

    ```sh
    pip install -r requirements.txt
    ```

1. Run the code

    ```sh
    python src/main.py
    ```

    You'll see a message like below. Push enter and recording for 5 seconds will be started. When you speak like 「リビングのライトを点けて」, your voice will be transformed to text and sent to the OpenAI model and the device will be turned on.

    To exit the interaction, enter 'q' key when the message is displayed.

    ```txt
    Enter to start recording for 5 seconds, q to exit:
    ```
