import os

local_ip = "192.168.200.108"
remote_lib_host = "192.168.200.108"
remote_lib_port = "8002"

sipp_A_remote_lib_port = "8050"
sipp_B_remote_lib_port = "8051"
sipp_C_remote_lib_port = "8052"

MVSIP_REMOTE_PATH = "/usr/protei/Protei-MV.SIP"
SBC_REMOTE_PATH = "/usr/protei/Protei-SBC/SBC"
MCU_REMOTE_PATH = "/usr/protei/Protei-SBC/MCU"
SBC_MCU_REMOTE_PATH = "/usr/protei/Protei-SBC"
CLI_REMOTE_PATH = "/usr/protei/CLI-Server/Server"
REMOTE_LIB_PATH = "%s/robot" % SBC_REMOTE_PATH


#ROBOTDIR = os.chdir("/../.." % os.getcwd())

ROBOTDIR = os.path.abspath('./../../..')
SCENARIO_PATH = "/usr/protei/Protei-SBC/SBC/robot/scenario"
#SCENARIO_PATH = "%s/implementation/resources/scenario/" % ROBOTDIR
EXECUTION_LIB_PATH = "%s/execution/lib/" % ROBOTDIR

COMMON_SETTINGS_FILE = "%s/implementation/resources/common_settings.txt" % ROBOTDIR
RECEIVED_PCMA_FILE = "%s/implementation/resources/received.pcma" % ROBOTDIR
SRC_PCMA_FILE = "%s/scenario_SBC/Transcode/uac_init_invite_A-B/pcap/received.pcma" % SCENARIO_PATH

