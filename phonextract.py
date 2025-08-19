#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from typing import Optional, Tuple

import phonenumbers
from phonenumbers import (
    geocoder,
    carrier,
    number_type,
    timezone,
    is_valid_number,
    region_code_for_number,
)

from colorama import init, Fore, Back, Style

init(autoreset=True)

# Optional: allow national numbers without '+' by setting a default region (ISO 3166-1 alpha-2)
# Example: DEFAULT_REGION = "IN" or "US"
DEFAULT_REGION: Optional[str] = None

TYPES = {
    0: "FIXED_LINE",
    1: "MOBILE",
    2: "FIXED_LINE_OR_MOBILE",
    3: "TOLL_FREE",
    4: "PREMIUM_RATE",
    5: "SHARED_COST",
    6: "VOIP",
    7: "PERSONAL_NUMBER",
    8: "PAGER",
    9: "UAN",
    10: "VOICEMAIL",
    27: "UNKNOWN",
}


def clear_screen() -> None:
    """Clears the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def gradient_line(width: int = 60) -> str:
    colors = [Fore.RED, Fore.MAGENTA, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE]
    seg = max(1, width // len(colors))
    parts = []
    for i, c in enumerate(colors):
        parts.append(c + "━" * (seg if i < len(colors) - 1 else width - seg * (len(colors) - 1)))
    return "".join(parts) + Style.RESET_ALL


def banner() -> None:
    line = gradient_line(64)
    print(line)
    title = f"{Fore.CYAN}{Style.BRIGHT}📞 PhoneXtract — Number Intelligence Tool{Style.RESET_ALL}"
    subtitle = f"{Fore.YELLOW}🛡️ For Educational and OSINT Purposes Only{Style.RESET_ALL}"
    author = f"{Fore.MAGENTA}🔧 Created by: Alok Thakur{Style.RESET_ALL}"
    credit = f"{Fore.WHITE}{Back.BLUE}{Style.BRIGHT} ✨ Made by Tp Editz ✨ {Style.RESET_ALL}"
    yt = f"{Fore.CYAN}📺 YouTube: Firewall Breaker{Style.RESET_ALL}"

    print(title.center(80))
    print(subtitle.center(80))
    print(author.center(80))
    print(yt.center(80))
    print(credit.center(80))
    print(line)


def footer() -> None:
    line = gradient_line(64)
    print(line)
    msg = f"{Fore.WHITE}{Back.BLUE}{Style.BRIGHT} Thank you for using PhoneXtract • Made by Tp Editz {Style.RESET_ALL}"
    print(msg.center(80))
    print(line)


def normalize_and_parse(user_input: str) -> Tuple[Optional[phonenumbers.PhoneNumber], Optional[str]]:
    """
    Normalize and parse the user input.
    Returns (parsed_number, error_message). If parsing fails, parsed_number is None and error_message is set.
    """
    s = (user_input or "").strip()
    if not s:
        return None, "Please enter a phone number."

    default_region = DEFAULT_REGION if DEFAULT_REGION else None

    if not s.startswith("+") and not default_region:
        return None, "Use E.164 with '+', e.g., +14155552671. Or set DEFAULT_REGION to allow national inputs."

    try:
        parsed = phonenumbers.parse(s, default_region)
    except phonenumbers.NumberParseException as e:
        return None, f"Parse error: {e}"

    return parsed, None


def info_row(label_icon: str, value: str, color=Fore.WHITE) -> None:
    lbl, icon = label_icon.split("|", 1)
    label = f"{Style.BRIGHT}{lbl.strip()}{Style.RESET_ALL}"
    icon = icon.strip()
    print(f"{color}{icon} {label}:{Style.RESET_ALL} {value}")


def analyze_number(user_input: str) -> None:
    parsed, err = normalize_and_parse(user_input)
    if err:
        print(Fore.RED + f"[!] {err}")
        return

    valid = is_valid_number(parsed)

    country_desc = geocoder.description_for_number(parsed, "en") or "Unknown"
    sim_car = carrier.name_for_number(parsed, "en") or "Unknown"
    ntype = number_type(parsed)
    tzs = timezone.time_zones_for_number(parsed) or ()
    region = region_code_for_number(parsed) or "Unknown"
    intl_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    natl_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    cc = parsed.country_code
    national = str(parsed.national_number)
    nlen = len(national)

    # Heuristic extras (not authoritative across all numbering plans)
    area_code = national[:3] if len(national) >= 3 else national
    prefix = national[:4] if len(national) >= 4 else national

    print("\n" + Fore.YELLOW + Style.BRIGHT + "[+] Phone Number Analysis" + Style.RESET_ALL)
    print(Fore.GREEN + "-" * 48)

    info_row("Location | 📍", country_desc, Fore.BLUE)
    info_row("Carrier | 📡", sim_car, Fore.RED)
    info_row("Type | 📞", TYPES.get(ntype, "UNKNOWN"), Fore.CYAN)
    info_row("Time Zone | 🕰️", (", ".join(tzs) if tzs else "Unknown"), Fore.MAGENTA)
    info_row("International Format | 🌍", intl_fmt, Fore.GREEN)
    info_row("National Format | 📞", natl_fmt, Fore.GREEN)

    info_row("Country Code | 🌎", str(cc), Fore.YELLOW)
    info_row("Number Length | 🔢", f"{nlen} digits", Fore.GREEN)
    info_row("Valid Number | ✔️", "Yes" if valid else "No", Fore.RED)
    info_row("Region Code | 🏙️", region, Fore.CYAN)
    info_row("Area Code (heuristic) | 📶", area_code, Fore.MAGENTA)
    info_row("Prefix (heuristic) | 🔠", prefix, Fore.YELLOW)

    print(Fore.GREEN + "-" * 48)

    # Honest placeholders (avoid misleading users)
    info_row("SIM Type | 💳", "Not available (carrier-specific)", Fore.GREEN)
    info_row("Call Type | 📞", "Context-dependent (not inferred)", Fore.CYAN)
    info_row("Risk/Spam/Breach | ⚠️", "Not available in this offline tool", Fore.RED)
    info_row("Carrier Known | 📡", "Yes" if sim_car != "Unknown" else "No", Fore.CYAN)
    info_row("Roaming | 🌍", "Check with the carrier", Fore.MAGENTA)

    print(Fore.GREEN + "-" * 48)


def main() -> None:
    while True:
        clear_screen()
        banner()
        prompt = "📲 Enter phone number (E.164, e.g., +14155552671): "
        if DEFAULT_REGION:
            prompt = f"📲 Enter phone number (E.164 or national for {DEFAULT_REGION}): "
        num = input(Fore.CYAN + prompt)

        print(Fore.CYAN + "⏳ Processing...")
        time.sleep(0.25)  # small UX delay
        analyze_number(num)

        print()
        cont = input(Fore.CYAN + "🔁 Do you want to check another number? (Y/N): ").strip().lower()
        if cont != "y":
            footer()
            break


if __name__ == "__main__":
    main()
    
