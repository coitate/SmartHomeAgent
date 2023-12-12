# Smart Home Agent

A Smart Home Agent using OpenAI API can recognize a user voice and instructions and control the devices of SwitchBot in the user home.

## Prerequisites

- To chat with verbally, a mic and speaker are needed.
- To use OpenAI API, an account is needed.
  - Before using OpenAI API, you need credits on the [Billing settings page](https://platform.openai.com/account/billing/overview).
- To call SwitchBot API, an account and TOKEN, API_KEY are needed.
  - <https://github.com/OpenWonderLabs/SwitchBotAPI#getting-started>
- Environment
  - Python: 3.11
  - OS: Windows (WSL: Ubuntu 22.04) and macOS Monterey are tested.
  - CPU: i5-12xxU (Win) and M1 Max (Mac) are tested.
  - Memory: 16 GB (Win) and 32 GB (Mac) are tested.

## Get to started

1. Install packages to use audio devices
   - Windows

     WIP.

   - Mac

     Install `portaudio`

     ```bash
     brew install portaudio
     ```

1. Set parameters

    Create the file `.env` in the repository root and its content is below. Replace the parameters with yours.

    ```txt
    SWITCHBOT_TOKEN={YOUR_TOKEN}
    SWITCHBOT_SECRET_KEY={YOUR_SECRET_KEY}
    ORGANIZATION_ID={YOUR_ORGANIZATION_ID}
    API_KEY={YOUR_API_KEY}
    ```

1. Create a virtual environment

    ```bash
    python -m venv .venv
    ```

1. Activate the virtual environment

    ```bash
    source .venv/bin/activate
    ```

    When deactivate, use `deactivate` command.

1. Install the dependency

    ```bash
    pip install -r requirements.txt
    ```

1. Run the code

    ```bash
    python src/main.py
    ```

    You'll see a message like below. Enter the instructions.

    ```txt
    Q:
    ```
