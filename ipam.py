#!/usr/bin/python

import json
import sys
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

IPAM_API = 'http://ipam-test.rzd/api/test/'
USERNAME = 'admin'
PASSWORD = 'P@ssw0rd'
SSL_VERIFY = True


def get_json(url):

    # Performs a GET using the passed URL location
    token = update_token(IPAM_API)
    r = requests.get(url, auth=(USERNAME, PASSWORD), headers={'token': token})
    return r.json()

def get_json_add(url):

    # Performs a GET using the passed URL location
    token = update_token(IPAM_API)
    r = requests.post(url, auth=(USERNAME, PASSWORD), headers={'token': token})
    return r.json()

def get_results_add(url):
    jsn = get_json_add(url)
    if jsn.get('error'):
        print 'Error: ' + jsn['error']['message']
    else:
        if jsn.get('results'):
            return jsn['results']
        elif 'results' not in jsn:
            return jsn
        else:
            print 'No results found'
    return None

def get_results(url):
    jsn = get_json(url)
    if jsn.get('error'):
        print 'Error: ' + jsn['error']['message']
    else:
        if jsn.get('results'):
            return jsn['results']
        elif 'results' not in jsn:
            return jsn
        else:
            print 'No results found'
    return None

def get_json_token(url):

    # Performs a GET using the passed URL location

    r = requests.post(url, auth=(USERNAME, PASSWORD), verify=SSL_VERIFY)
    return r.json()


def get_results_token(url):
    jsn = get_json_token(url)
    if jsn.get('error'):
        print 'Error: ' + jsn['error']['message']
    else:
        if jsn.get('results'):
            return jsn['results']
        elif 'results' not in jsn:
            return jsn
        else:
            print 'No results found'
    return None

def display_all_results(url):
    results = get_results(url)
    if results:
        print json.dumps(results, indent=4, sort_keys=True)


def update_token(url):
    url = url + 'user/'
    token = get_results_token(url)
    return token['data']['token']

def check(url, ip):
    url = url + '/addresses/search/' + ip + '/'
    result = get_results(url)
    try: 
        result = result['data'][0]['ip']
    except KeyError:
        return False
    else:
        return True

def checkSubnet(url, subnet):
	url = url + '/subnets/cidr/' + str(subnet)
	subnetCheck = get_results(url)
	if subnetCheck['success'] == True:
		print(subnetCheck['data'][0]['id'])
		return subnetCheck['data'][0]['id']
	else:
		return False

def addip(url,subnetid,ip):
	print(ip)
	url = url + '/addresses/?subnetId=' + str(subnetid) + '&ip=' + str(ip)
	result = get_results_add(url)
	if result['success'] == True:
		return True
	else:
		return False
def main():
	f = open('facts_ip', 'r')
	log = open('added_ip', 'w')
	ips = list()
	existingSubs = {}
	notexistingSubs = list()
	for line in f:
		isExist = True
		curhost = line.split(' ')
		curhost[2] = curhost[2].replace('\n', '')
		checkIP = check(IPAM_API, curhost[1])
		if checkIP == False:
			try:
				curId = existingSubs[curhost[2]]
			except KeyError:

				for i in notexistingSubs:
					if i == curhost[2]:
						isExist = False
						break

				if isExist == True:
					checkSub = checkSubnet(IPAM_API, curhost[2])
					if checkSub == False:
						err="Subnet " + str(curhost[2]) + " doesn't exists"
						print(err)
						notexistingSubs.append(curhost[2])
					else:
						existingSubs[curhost[2]] = checkSub
						curId = checkSub
						curIp = curhost[1]
						addingip=addip(IPAM_API,curId,curIp)
						if addingip == True:
							print(str(curIp) + ' has been added')
							log.write(str(curIp) + ' has been added to subnet ' + str(curhost[2]) + ' with id ' + str(curId) + '\n')
						else:
							print(str(curIp) + " wasn't added")
			else:
				curId = checkSub
				curIp = curhost[1]
				addingip=addip(IPAM_API,curId,curIp)
				if addingip == True:
					print(str(curIp) + ' has been added')
					log.write(str(curIp) + ' has been added to subnet ' + str(curhost[2]) + ' with id ' + str(curId) + '\n')
				else:
					print(str(curIp) + " wasn't added")
	log.write(notexistingSubs)
	f.close()
	log.close()
if __name__ == '__main__':
    main()