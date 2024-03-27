from rich import print


def logger(self, value: str, type: str = "default") -> None:
    if self.logs is False:
        return None

    log_value = f"<{self.layer}> {value}"

    if type == "success":
        print("[bold green]SUCCESS:", log_value)
        return 0

    if type == "error":
        print("[bold red]ERROR:", log_value)
        return 0

    if type == "warning":
        print("[bold dark_orange]WARNING:", log_value)
        return 0

    print("[bold]INFO:", log_value)
    return 0
