from uvicorn import run


def main():
    run("api_entry:api", host="127.0.0.1", port=116, reload=True)


if __name__ == "__main__":
    main()
