#!/usr/bin/env python3
"""Vremenska prognoza za Čačak.

Koristi besplatni Open-Meteo API (https://open-meteo.com), nije potreban API ključ.
Radi samo sa standardnom bibliotekom Pythona.

Upotreba:
    python3 prognoza_cacak.py            # trenutno vreme + prognoza za 7 dana
    python3 prognoza_cacak.py --dana 3   # prognoza za 3 dana (1 do 16)
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import date

GRAD = "Čačak"
LATITUDA = 43.8914
LONGITUDA = 20.3497
API_URL = "https://api.open-meteo.com/v1/forecast"

DANI_U_NEDELJI = ["Ponedeljak", "Utorak", "Sreda", "Četvrtak", "Petak", "Subota", "Nedelja"]

# WMO kodovi vremenskih uslova
OPIS_VREMENA = {
    0: "Vedro",
    1: "Pretežno vedro",
    2: "Delimično oblačno",
    3: "Oblačno",
    45: "Magla",
    48: "Magla sa injem",
    51: "Slaba rosulja",
    53: "Umerena rosulja",
    55: "Jaka rosulja",
    56: "Slaba ledena rosulja",
    57: "Jaka ledena rosulja",
    61: "Slaba kiša",
    63: "Umerena kiša",
    65: "Jaka kiša",
    66: "Slaba ledena kiša",
    67: "Jaka ledena kiša",
    71: "Slab sneg",
    73: "Umeren sneg",
    75: "Jak sneg",
    77: "Snežna zrna",
    80: "Slabi pljuskovi",
    81: "Umereni pljuskovi",
    82: "Jaki pljuskovi",
    85: "Slabi snežni pljuskovi",
    86: "Jaki snežni pljuskovi",
    95: "Grmljavina",
    96: "Grmljavina sa slabim gradom",
    99: "Grmljavina sa jakim gradom",
}

SMEROVI_VETRA = ["S", "SI", "I", "JI", "J", "JZ", "Z", "SZ"]


def opis(kod):
    return OPIS_VREMENA.get(kod, f"Nepoznato ({kod})")


def smer_vetra(stepeni):
    return SMEROVI_VETRA[round(stepeni / 45) % 8]


def preuzmi_prognozu(dana):
    parametri = {
        "latitude": LATITUDA,
        "longitude": LONGITUDA,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,"
                   "weather_code,wind_speed_10m,wind_direction_10m,pressure_msl",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                 "precipitation_sum,precipitation_probability_max,wind_speed_10m_max",
        "timezone": "Europe/Belgrade",
        "forecast_days": dana,
    }
    url = f"{API_URL}?{urllib.parse.urlencode(parametri)}"
    with urllib.request.urlopen(url, timeout=15) as odgovor:
        return json.load(odgovor)


def prikazi(podaci):
    t = podaci["current"]
    print(f"=== Vremenska prognoza za {GRAD} ===\n")
    print(f"Trenutno ({t['time'].replace('T', ' ')}):")
    print(f"  {opis(t['weather_code'])}")
    print(f"  Temperatura:   {t['temperature_2m']:.1f} °C "
          f"(oseća se kao {t['apparent_temperature']:.1f} °C)")
    print(f"  Vlažnost:      {t['relative_humidity_2m']} %")
    print(f"  Vetar:         {t['wind_speed_10m']:.1f} km/h, {smer_vetra(t['wind_direction_10m'])}")
    print(f"  Pritisak:      {t['pressure_msl']:.0f} hPa\n")

    d = podaci["daily"]
    print("Prognoza po danima:")
    print(f"  {'Dan':<18}{'Min':>6}{'Max':>6}{'Padavine':>12}{'Vetar':>11}  Opis")
    print("  " + "-" * 78)
    for i, datum_str in enumerate(d["time"]):
        datum = date.fromisoformat(datum_str)
        dan = f"{DANI_U_NEDELJI[datum.weekday()]} {datum:%d.%m.}"
        verovatnoca = d["precipitation_probability_max"][i]
        padavine = f"{d['precipitation_sum'][i]:.1f}mm"
        if verovatnoca is not None:
            padavine += f" {verovatnoca}%"
        print(f"  {dan:<18}"
              f"{d['temperature_2m_min'][i]:>5.0f}°"
              f"{d['temperature_2m_max'][i]:>5.0f}°"
              f"{padavine:>12}"
              f"{d['wind_speed_10m_max'][i]:>7.0f}km/h"
              f"  {opis(d['weather_code'][i])}")


def main():
    parser = argparse.ArgumentParser(description=f"Vremenska prognoza za {GRAD}")
    parser.add_argument("--dana", type=int, default=7, choices=range(1, 17),
                        metavar="N", help="broj dana prognoze (1 do 16, podrazumevano 7)")
    args = parser.parse_args()

    try:
        podaci = preuzmi_prognozu(args.dana)
    except Exception as greska:
        print(f"Greška pri preuzimanju prognoze: {greska}", file=sys.stderr)
        sys.exit(1)

    prikazi(podaci)


if __name__ == "__main__":
    main()
