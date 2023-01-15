def format_thousands(number):
	return f'{int(number):,}'.replace(',', ' ')


def reduce_number(num, precision = 2, suffixes = ('', 'K', 'M', 'G', 'T', 'P')):
	m = sum([abs(num / 1000.0 ** x) >= 1 for x in range(1, len(suffixes))])
	return f'{num/1000.0**m:.{precision}f}{suffixes[m]}'


def highlight_percentage(done_percent):
	done_percent = float(done_percent)
	if done_percent < 20:
		return 'background-color: rgb(247,252,245)'
	if done_percent < 50:
		return 'background-color: rgb(199,233,192)'
	if done_percent < 80:
		return 'background-color: rgb(116,196,118)'
	if done_percent < 100:
		return 'background-color: rgb(35,139,69)'
	if done_percent == 100:
		return 'background-color: rgb(0,109,44)'
