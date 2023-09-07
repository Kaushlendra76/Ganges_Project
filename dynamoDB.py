import boto3
import time

class dynamoDB():
    def __init__(self):
################## key variables ###################
        self.uid="2"  #needs to be changed for every iteration 
        self.id=11
        self.did='13A20041B4E6B2'
        self.cmd='101C'
        self.battery_charging=46
        self.battery_discharging=2
        self.battery_state_of_charge=100
        self.battery_temp=30
        self.battery_volt=27
        self.charge_controller_temperature=30
        self.controller_status="TRUE"
        self.generated_energy=0
        self.pv_current=3
        self.pv_power=0
        self.pv_volt=26
        self.pv_work_status="TRUE"
        self.timestamp='Null'
        ####################################################

        self.aws_access_key_id = 'AKIA57CK6FWMRBJLPFVO'
        self.aws_secret_access_key = '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'
        self.__Tablename__="Ganges_node_101C"
        self.client=boto3.client('dynamodb',"ap-south-1",aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
        self.db=boto3.resource('dynamodb',"ap-south-1", aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
        
    def updateDB(self):
        table=self.db.Table(self.__Tablename__)
        item = {
        'uid': self.uid,
            'Server_sl.no': 14,
            'did': self.did,
            'cmd': self.cmd,
            'battery_charging': self.battery_charging,
            'battery_discharging':self.battery_discharging,
            'battery_state_of_charge':self.battery_state_of_charge,
            'battery_temp':self.battery_temp,
            'battery_volt':self.battery_volt,
            'charge_controller_temperature':self.charge_controller_temperature,
            'controller_status':self.controller_status,
            'generated_energy': self.generated_energy,
            'pv_current':self.pv_current,
            'pv_power':self.pv_power,
            'pv_volt':self.pv_volt,
            'pv_work_status':self.pv_work_status,
            'timestamp': self.timestamp   
        }

        response = table.put_item(Item=item,)

        print(response)
if __name__ == "__main__":
    print("uploading data")
    dyDB=dynamoDB()
    dyDB.updateDB()