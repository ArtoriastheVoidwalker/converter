import os
import csv

import xml.etree.ElementTree as ET

from loguru import logger


def import_data(import_file: str) -> list:
    data = []
    tree = ET.parse(import_file)
    root = tree.getroot()

    file_name_xml = import_file
    date_xml = root[0][0][0][1].text

    check_list = []
    for check_xml in root[1]:
        check_list.append(check_xml[0].text)

    name_list = []
    for name_xml in root[1]:
        name_list.append(name_xml[1].text)

    address_list = []
    for address_xml in root[1]:
        address_list.append(address_xml[2].text)

    period_list = []
    for period_xml in root[1]:
        period_list.append(period_xml[3].text)

    sum_list = []
    for sum_xml in root[1]:
        sum_list.append(sum_xml[4].text)

    personal_accounts = {}
    for i in range(len(check_list)):
        if check_list[i] in personal_accounts and period_list[i] == personal_accounts[check_list[i]]:
            personal_accounts.pop(check_list[i])
            logger.error(f"There are duplicate records: {check_list[i]}:{period_list[i]} )")
        else:
            personal_accounts[check_list[i]] = period_list[i]
    name_list = removing_duplicates(name_list)
    address_list = removing_duplicates(address_list)
    check_list = [a for a in personal_accounts.keys()]
    period_list = [a for a in personal_accounts.values()]
    sum_list = removing_duplicates(sum_list)

    data.append(file_name_xml)
    logger.info(f"Registry file name: {file_name_xml}")
    data.append(date_xml)
    logger.info(f"Data relevance date: {date_xml}")
    data.append(check_list)
    logger.info(f"Personal accounts: {check_list}")
    data.append(name_list)
    logger.info(f"Full names: {name_list}")
    data.append(address_list)
    logger.info(f"Address: {address_list}")
    data.append(period_list)
    logger.info(f"Periods: {period_list}")
    data.append(sum_list)
    logger.info(f"Sums: {sum_list}")

    os.rename(import_file, f"./arh/{import_file}")
    logger.info("Data import completed")
    logger.info("-----------------------------------"
                "----------------------------------------------------\n")
    export_data(data)
    return data


def export_data(data: list):
    file_name = data[0]
    date = data[1]
    check_list = data[2]
    name_list = data[3]
    address_list = data[4]
    period_list = data[5]
    sum_list = data[6]
    min = 0

    with open("result.csv", "w", encoding="windows-1251") as file:
        writer = csv.writer(file)
        for x in range(len(check_list)):
            if check_list[min] or period_list[min] is None:
                logger.error(f"Required attribute not found. "
                             f"Personal account or Period №{min+1} is None")

            if int(date.split('.')[0]) > 31 or int(date.split('.')[1]) > 12:
                logger.error("Invalid date format")

            if 0 > int(str(period_list[0])[:2]
                       or int(str(period_list[min])[:2]) < 13):
                period_list[min] = None
                logger.error("Incorrect day or month format in the period")

            if 0 > float(sum_list[min]) \
                    and len(str(float(sum_list[min])).split('.')[1]) > 2:
                logger.error("The number of decimal places is higher than the allowed value")
                sum_list[min] = None
            writer.writerow(
                (
                    file_name,
                    date,
                    check_list[min],
                    name_list[min],
                    address_list[min],
                    int(period_list[min]),
                    float(sum_list[min])

                ))
            logger.info(
                "Data add in result.csv\n"
                f"Registry file name: {file_name}\n"
                f"Data relevance date: {date}\n"
                f"Personal account: {check_list[min]}\n"
                f"Full name: {name_list[min]}\n"
                f"Address: {address_list[min]}\n"
                f"Period: {int(period_list[min])}\n"
                f"Sum: {float(sum_list[min])}\n")
            min += 1

    logger.info("Data export completed")
    logger.info("-----------------------------------"
                "----------------------------------------------------\n")


def validation(import_file: str):
    if import_file.rpartition('.')[2] != 'xml':
        logger.error("File type error. Processing is not possible.")
        os.rename(import_file, f"./bad/{import_file}")
    else:
        import_data(import_file)


def removing_duplicates(list_items):
    temp = []
    for x in list_items:
        if x not in temp:
            temp.append(x)
        else:
            temp.pop(temp.index(x))
    ints_list = temp
    return ints_list


if __name__ == '__main__':
    import_file = input()
    logger.add("./log/logger.log", format="{time} {level} {message}",
               level="INFO", rotation="1 MB", compression="zip")
    validation(import_file)
