def format_thousands(number: str) -> str:
	try:
		return f'{int(number):,}'.replace(',', ' ')
	except ValueError:
		return '0'


def reduce_number(
	num: float,
	precision: int = 2,
	suffixes: tuple[str, str, str, str, str, str] = ('', 'K', 'M', 'G', 'T', 'P'),
) -> str:
	m = sum([abs(num / 1000.0 ** x) >= 1 for x in range(1, len(suffixes))])
	return f'{num/1000.0**m:.{precision}f}{suffixes[m]}'


def highlight_percentage(done_percent: str) -> str:
	done_percent_float: float = float(done_percent)
	if done_percent_float < 20:
		return 'background-color: rgb(247,252,245)'
	if done_percent_float < 50:
		return 'background-color: rgb(199,233,192)'
	if done_percent_float < 80:
		return 'background-color: rgb(116,196,118)'
	if done_percent_float < 100:
		return 'background-color: rgb(35,139,69)'
	if done_percent_float == 100:
		return 'background-color: rgb(0,109,44)'
	return ''
