import pandas as pd
from io import StringIO
import numpy as np

def from_string(csv_string: str) -> pd.DataFrame:
	data = StringIO(csv_string.replace(',\n','\n'))
	df = pd.read_csv(data, names=['Report','Symbol','Side','Size','OpenPrice','ClosePrice','PNL','EntryTime','ExitTime','TestTime','DD','x'])
	for i in list(df.columns):
		if 'time' in i.lower():
			df[i] = pd.to_datetime(df[i])
	df['Side'] = df.Side.replace(0,'Sell').replace(1,'Buy').values
	return df

def trading_metrics(df):
	total_trades = len(df)
	winning_trades = df[df['PNL'] > 0]
	losing_trades = df[df['PNL'] < 0]
	
	num_winning_trades = len(winning_trades)
	num_losing_trades = len(losing_trades)
	
	total_profit = winning_trades['PNL'].sum()
	total_loss = losing_trades['PNL'].sum()
	
	average_profit = total_profit / num_winning_trades if num_winning_trades > 0 else 0
	average_loss = total_loss / num_losing_trades if num_losing_trades > 0 else 0
	
	net_profit = df['PNL'].sum()
	
	win_rate = num_winning_trades / total_trades if total_trades > 0 else 0
	loss_rate = num_losing_trades / total_trades if total_trades > 0 else 0
	
	average_win = winning_trades['PNL'].mean() if num_winning_trades > 0 else 0
	average_loss_value = losing_trades['PNL'].mean() if num_losing_trades > 0 else 0
	
	largest_win = winning_trades['PNL'].max() if num_winning_trades > 0 else 0
	largest_loss = losing_trades['PNL'].min() if num_losing_trades > 0 else 0
	
	profit_factor = total_profit / abs(total_loss) if total_loss != 0 else np.inf
	
	# Average trade duration
	df['EntryTime'] = pd.to_datetime(df['EntryTime'])
	df['ExitTime'] = pd.to_datetime(df['ExitTime'])
	average_trade_duration = (df['ExitTime'] - df['EntryTime']).mean()

	# Max drawdown
	max_drawdown = df['DrawDown'].max() if 'DrawDown' in df.columns else 0

	# Sharpe Ratio
	if 'PNL' in df.columns:
		returns = df['PNL']
		mean_return = returns.mean()
		return_std = returns.std()
		sharpe_ratio = (mean_return / return_std) * np.sqrt(252) if return_std != 0 else np.inf
	else:
		sharpe_ratio = np.inf

	# Risk of Ruin
	# Assuming a simple risk of ruin calculation based on average win and loss
	if average_loss_value < 0:
		risk_of_ruin = (average_loss_value / (average_loss_value + average_win)) ** num_winning_trades if average_win + average_loss_value != 0 else 1
	else:
		risk_of_ruin = 0

	metrics = {
		'Number of Total Trades': total_trades,
		'Number of Winning Trades': num_winning_trades,
		'Number of Losing Trades': num_losing_trades,
		'Profit Factor': profit_factor,
		'Average Trade Duration': average_trade_duration.seconds/3600,
		'Max Drawdown': max_drawdown,
		'Total Profit': total_profit,
		'Total Loss': total_loss,
		'Average Profit': average_profit,
		'Average Loss': average_loss,
		'Net Profit': net_profit,
		'Risk of Ruin': risk_of_ruin,
		'Sharpe Ratio': sharpe_ratio,
		'Win Rate': win_rate,
		'Loss Rate': loss_rate,
		'Average Win': average_win,
		'Average Loss': average_loss_value,
		'Largest Win': largest_win,
		'Largest Loss': largest_loss,
	}

	return metrics
	
	

def calculate_timely_metrics(df):
	# Ensure EntryTime and ExitTime are in datetime format
	df['Duration'] = (df['ExitTime'] - df['EntryTime']).dt.seconds/3600

	# Extract hour and day of week
	df['Hour'] = df['EntryTime'].dt.hour
	df['WeekDay'] = df['EntryTime'].dt.day_name()

	# Define a helper function to calculate win rate
	def win_rate(group):
		wins = (group['PNL'] > 0).sum()
		total = group['PNL'].count()
		return wins / total if total > 0 else np.nan

	# Hourly metrics
	hourly_groups = df.groupby('Hour')
	hourly_win_rate = hourly_groups.apply(win_rate)
	hourly_pnl = hourly_groups['PNL'].mean()
	hourly_number_of_trades = hourly_groups.size()
	hourly_volume = hourly_groups['Size'].mean()

	# Week Day metrics
	weekday_groups = df.groupby('WeekDay')
	weekday_win_rate = weekday_groups.apply(win_rate)
	weekday_pnl = weekday_groups['PNL'].mean()
	weekday_number_of_trades = weekday_groups.size()
	weekday_volume = weekday_groups['Size'].mean()

	# Combine results into dataframes
	hourly_metrics = pd.DataFrame({
		'Hourly Win Rate': hourly_win_rate,
		'Hourly PnL': hourly_pnl,
		'Hourly Number of Trades': hourly_number_of_trades,
		'Hourly Volume': hourly_volume
	})

	weekday_metrics = pd.DataFrame({
		'Week Day Win Rate': weekday_win_rate,
		'Week Day PnL': weekday_pnl,
		'Week Day Number of Trades': weekday_number_of_trades,
		'Week Day Volume': weekday_volume
	})

	return hourly_metrics, weekday_metrics
