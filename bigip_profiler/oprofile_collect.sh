#!/bin/bash
 
SESSION_DIR="$1"
SAMPLE_ITERATIONS="$2"
SAMPLE_DURATION="$3"
 
: ${SESSION_DIR:=/shared/profiling_data}
: ${SAMPLE_ITERATIONS:=6}
: ${SAMPLE_DURATION:=10}
 
COMMAND_LOG="${SESSION_DIR}/command.log"
 
rm -rf ${SESSION_DIR}
mkdir -p ${SESSION_DIR}
rm -f ${COMMAND_LOG}
 
echo "Logging commands to ${COMMAND_LOG}"
 
timestamp() {
    TZ=UTC date '+%Y-%m-%dT%H:%M:%SZ'
}
 
log() {
   echo $(timestamp) $* >> ${COMMAND_LOG}
}
 
opcontrol() {
    log opcontrol $*
    /usr/bin/opcontrol $*
}
 
modprobe() {
    log modprobe $*
    /sbin/modprobe $*
}
 
is_virtual_platform() {
    halid | egrep -q '^Info:system_id\s*=\s*Z[0-9]'
    return $?
}
 
NMI_WATCHDOG_PATH=/proc/sys/kernel/nmi_watchdog
_NMI_WATCHDOG_VALUE=$(<${NMI_WATCHDOG_PATH})
disable_nmi_watchdog() {
    log "echo 0 > ${NMI_WATCHDOG_PATH}"
    echo 0 > ${NMI_WATCHDOG_PATH}
}
 
enable_nmi_watchdog() {
    log "echo ${_NMI_WATCHDOG_VALUE} > ${NMI_WATCHDOG_PATH}"
    echo ${_NMI_WATCHDOG_VALUE} > ${NMI_WATCHDOG_PATH}
}
 
oprofile_init() {
    disable_nmi_watchdog
    opcontrol --deinit
    if is_virtual_platform; then
        echo "Virtual platform detected.  Loading oprofile module in timer mode."
        modprobe oprofile timer=1
    else
        echo "Loading oprofile module."
        opcontrol --init
    fi
    opcontrol --setup \
              --no-vmlinux \
              --session-dir=${SESSION_DIR} \
              --separate=cpu,lib
}
 
oprofile_shut() {
    opcontrol --shutdown
    enable_nmi_watchdog
}
 
start_profiling() {
    opcontrol --start
}
 
stop_profiling() {
    opcontrol --stop
}
 
function save_session {
    target="$1"
    : ${target:="$(timestamp)"}
    opcontrol --save=${target}
}
 
oprofile_init
 
start_profiling
for s in $(seq ${SAMPLE_ITERATIONS}); do
    sleep ${SAMPLE_DURATION}
    save_session
done
stop_profiling
 
oprofile_shut
echo "Done.  Profiling data can be found in ${SESSION_DIR}"