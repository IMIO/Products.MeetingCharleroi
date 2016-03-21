## Script (Python) "checkFDAdviceIsTimedOut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dirfin

adviceInfos = dict(context.getAdviceDataFor(dirfin))
delayLabel = adviceInfos['delay_label']
adviceGivenOn = adviceInfos['advice_given_on']
delayInfos = adviceInfos['delay_infos']
delayStatus = delayInfos['delay_status']
delayStatusWhenStopped = delayInfos['delay_status_when_stopped']

if delayLabel.startswith('Avis DF >=') and adviceGivenOn is None and delayStatus == 'no_more_giveable':
    return True
else:
    return False
