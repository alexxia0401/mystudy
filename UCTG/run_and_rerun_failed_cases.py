#!/usr/bin/env python3

import os
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import date


def generate_run_file(test_plan, index):  # mpp-icmpv6
    handle = open('/tmp/codenomicon_run.txt', 'w')
    command = f'java -jar /opt/Synopsys/Defensics/monitor/boot.jar --testplan /root/synopsys/defensics/testplans/{test_plan}.testplan'
    handle.write(command)
    handle.write(' --index "')
    handle.write(index)
    handle.write('"')
    handle.close()

    os.chmod('/tmp/codenomicon_run.txt', 0o777)  # give execute permission


def get_failed_case_id(file_path):  # /tmp/log.txt
    handle = open(file_path, 'r')
    log_list = handle.readlines()  # return a list
    handle.close()
    log = ''.join(log_list)  # convert to string
    result_file_line = re.findall(r'Result files for.*', log)  # return a list that contains string
    result_file_path = re.findall(r'/root/.*', result_file_line[0])  # ending part contains a "
    result_file_path = result_file_path[0]
    result_file_path = result_file_path.replace('"',
                                                '')  # e.g. /root/synopsys/defensics/results/ICMPv6/20201124-0038-58
    summary_xml = result_file_path + '/' + 'summary.xml'
    print("Found summary file:", summary_xml)
    failed_cases = []
    tree = ET.ElementTree(file=summary_xml)
    for elem in tree.iterfind('collection/fact'):
        # print(elem.text)
        failed_id_list = re.findall(r'^\d+', elem.text)  # e.g. ['3']
        failed_id_str = failed_id_list[0]  # e.g. '3'
        failed_id_int = int(failed_id_str)  # e.g. 3
        failed_cases.append(failed_id_int)
    return failed_cases


test_round = 1
SPLIT_NUMBER = 20000
PASS_NUMBER = 200
TEST_PLAN = 'mpp-tcp-serverv6'

handle = open('/tmp/log.txt', 'w')
#subprocess.run('/tmp/codenomicon_bash_100.txt', stdout=handle, shell=True)  # start test
subprocess.run(f'java -jar /opt/Synopsys/Defensics/monitor/boot.jar --testplan /root/synopsys/defensics/testplans/{TEST_PLAN}.testplan', stdout=handle, shell=True)  # start test
handle.close()

tmp_list = []
handle = open('/tmp/log.txt', 'r')
for line in handle:
    tmp_list.append(line)
handle.close()

today = date.today()
today_str = today.strftime('%Y%m%d')
handle = open(f'/tmp/{TEST_PLAN}_log_{today_str}.txt', 'a')
for i in tmp_list:
    handle.write(i)
handle.close()

failed_cases = get_failed_case_id('/tmp/log.txt')


print("Failed count:", len(failed_cases))

if len(failed_cases) <= PASS_NUMBER:
    test_round = -1  # quit loop
    print(f"Cases <= {PASS_NUMBER}, stop running")
else:
    test_round += 1
    to_run_cases = {}
    n = 0
    if len(failed_cases) <= SPLIT_NUMBER:
        # no need to split, just run again
        to_run_cases[n] = failed_cases
    else:
        while len(failed_cases) > SPLIT_NUMBER:
            to_run_cases[n] = failed_cases[0:SPLIT_NUMBER]
            del failed_cases[0:SPLIT_NUMBER]
            n += 1
        else:
            to_run_cases[n] = failed_cases

while test_round > 1:
    tmp_total_failed_cases = []
    # run split cases
    for i in to_run_cases:
        # print(i, to_run_cases[i])
        print(f"run round {i+1}")
        index = ','.join([str(x) for x in to_run_cases[i]])

        generate_run_file(TEST_PLAN, index)

        handle = open('/tmp/log.txt', 'w')
        subprocess.run('/tmp/codenomicon_run.txt', stdout=handle, shell=True)  # start test
        handle.close()

        tmp_list = []
        handle = open('/tmp/log.txt', 'r')
        for line in handle:
            tmp_list.append(line)
        handle.close()

        handle = open(f'/tmp/{TEST_PLAN}_log.txt', 'a')
        for i in tmp_list:
            handle.write(i)
        handle.close()


        split_test_result = get_failed_case_id('/tmp/log.txt')

        tmp_total_failed_cases.extend(split_test_result)  # equivalent to failed_cases

    print("Failed count:", len(tmp_total_failed_cases))

    if len(tmp_total_failed_cases) <= PASS_NUMBER:
        test_round = -1  # quit loop
        print(f"Cases <= {PASS_NUMBER}, stop running")
    else:
        test_round += 1
        to_run_cases = {}
        n = 0
        if len(tmp_total_failed_cases) <= SPLIT_NUMBER:
            # no need to split, just run again
            to_run_cases[n] = tmp_total_failed_cases
        else:
            while len(tmp_total_failed_cases) >= SPLIT_NUMBER:
                to_run_cases[n] = tmp_total_failed_cases[0:SPLIT_NUMBER]
                del tmp_total_failed_cases[0:SPLIT_NUMBER]
                n += 1
            else:
                to_run_cases[n] = tmp_total_failed_cases
