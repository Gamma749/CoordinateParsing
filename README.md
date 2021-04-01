# CoordParsing

## Author: Hayden McAlister 1663787

## Running the Program
* From the terminal, run `python3 main.py [-v] [-f filepath]`
    * Running without the `-f filepath` flag will prompt for input from `stdin`, one coordinate pair per line. Type "EXIT" or press CTRL+C for a keyboard interrupt to stop entering coordinates
    * Running with the `-f filepath` flag will read coordinate pairs one per line from the file specified at `filepath`
    * Running with the `-v` flag enters verbose mode, where extra messages about the parsing process will be printed to `stdout`. This is mainly for testing purposes, or to better understand how the inputs are interpreted.

## Output
`main.py` creates and saves `data_file.geojson`, a geoJSON object containing a feature collection of each coordinate given to `main.py`. This can be visualized at `https://geojson.io/`

Note that running `main.py` will overwrite an existing  `data_file.geojson` so if you want to save a previous file, rename it or move it. No prompts are given, your data will be lost!

`data_file.geojson` is only written to AFTER all data is read and the input is closed by using CTRL+D, CTRL+C, or typing "EXIT"

## Testing
Testing has been done by using `testing.py` which takes data from `test_data.txt` and parses it through a `CoordParser` object. These tests are done in batches which fit a theme (such as standard form, invalid separators, etc...). Setting breakpoints in a debugger can allow for each parse output to be checked at a time, or to skip some sections entirely.