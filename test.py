from datetime import datetime



old_date = "Jun 20, 10:32 PM"
formatted_old_date = datetime.strptime(old_date.split(",")[0], "%b %d")
today = datetime.today()
formatted_old_date = formatted_old_date.replace(year=today.year)


print(today - formatted_old_date)