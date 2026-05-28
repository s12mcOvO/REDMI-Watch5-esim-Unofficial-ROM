set +e
setprop ota.progress.current 30
setprop ota.progress.next 30
echo " "
xr_efuse_get_version -r 1
if [ $? -ne 0 ]
then
    echo "efuse fbl version read failed"
else
    echo "  --fbl_version read success"
fi

xr_efuse_get_version -r 2
if [ $? -ne 0 ]
then
    echo "efuse sbl version read failed"
else
    echo "  --sbl_version read success"
fi

xr_efuse_get_version -r 3
if [ $? -ne 0 ]
then
    echo "efuse system version read failed"
else
    echo "  --sys_version read success"
fi
echo " "

echo "new fbl version is "0
if [ 0 -lt $fbl_version_current ]
then
    echo "check fbl version failed!"
else
    echo "fbl version check pass"
fi
setprop ota.fblversion.next 0

echo "new sbl version is "0
if [ 0 -lt $sbl_version_current ]
then
    echo "check sbl version failed!"
else
    echo "sbl version check pass"
fi
setprop ota.sblversion.next 0

echo "new system version is "0
if [ 0 -lt $sys_version_current ]
then
    echo "check system version failed!"
else
    echo "system version check pass"
fi
setprop ota.sysversion.next 0

xr_hw_id
set hw_id_flag $?
echo " -- hw id -- "
if [ $hw_id_flag -lt 0 ]
then
    echo "read hw_id failed!"
fi
echo " hw id -- "
echo $hw_id_flag


if [ ! -e /dev/CP ]
then
    echo "/dev/CP doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/CP_boot ]
then
    echo "/dev/CP_boot doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/CP_f ]
then
    echo "/dev/CP_f doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/CPbootf ]
then
    echo "/dev/CPbootf doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/CRF ]
then
    echo "/dev/CRF doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/CRF_f ]
then
    echo "/dev/CRF_f doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/IPC_DB ]
then
    echo "/dev/IPC_DB doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/ap ]
then
    echo "/dev/ap doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/ap_f ]
then
    echo "/dev/ap_f doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/app ]
then
    echo "/dev/app doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/dl_nv_d ]
then
    echo "/dev/dl_nv_d doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/dl_nv_d_bak ]
then
    echo "/dev/dl_nv_d_bak doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/dsp ]
then
    echo "/dev/dsp doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/dsp_f ]
then
    echo "/dev/dsp_f doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/font ]
then
    echo "/dev/font doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/i18n ]
then
    echo "/dev/i18n doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/mg_nv ]
then
    echo "/dev/mg_nv doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/mg_nv_1 ]
then
    echo "/dev/mg_nv_1 doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/misc ]
then
    echo "/dev/misc doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/mmap ]
then
    echo "/dev/mmap doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/quickapp ]
then
    echo "/dev/quickapp doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/sbl ]
then
    echo "/dev/sbl doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/sbl_bak ]
then
    echo "/dev/sbl_bak doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/sensor ]
then
    echo "/dev/sensor doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/sensor_f ]
then
    echo "/dev/sensor_f doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/system ]
then
    echo "/dev/system doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/tee ]
then
    echo "/dev/tee doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/tee_f ]
then
    echo "/dev/tee_f doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/vendor ]
then
    echo "/dev/vendor doesn't exist, will reboot to the old system"
    exit
fi

if [ ! -e /dev/watchface ]
then
    echo "/dev/watchface doesn't exist, will reboot to the old system"
    exit
fi

echo -e -n "a" > /data/ota_tmp/dd

echo "install vela_CP.bin"
time " dd if=/ota/vela_CP.bin of=/dev/CP bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_CP.bin failed"
    exit
fi
setprop ota.progress.current 30
setprop ota.progress.next 30

echo "install vela_CP_boot.bin"
time " dd if=/ota/vela_CP_boot.bin of=/dev/CP_boot bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_CP_boot.bin failed"
    exit
fi
setprop ota.progress.current 30
setprop ota.progress.next 31

echo "install vela_CP_f.bin"
time " dd if=/ota/vela_CP_f.bin of=/dev/CP_f bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_CP_f.bin failed"
    exit
fi
setprop ota.progress.current 31
setprop ota.progress.next 31

echo "install vela_CPbootf.bin"
time " dd if=/ota/vela_CPbootf.bin of=/dev/CPbootf bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_CPbootf.bin failed"
    exit
fi
setprop ota.progress.current 31
setprop ota.progress.next 31

echo "install vela_CRF.bin"
time " dd if=/ota/vela_CRF.bin of=/dev/CRF bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_CRF.bin failed"
    exit
fi
setprop ota.progress.current 31
setprop ota.progress.next 31

echo "install vela_CRF_f.bin"
time " dd if=/ota/vela_CRF_f.bin of=/dev/CRF_f bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_CRF_f.bin failed"
    exit
fi
setprop ota.progress.current 31
setprop ota.progress.next 31

echo "install vela_IPC_DB.bin"
time " dd if=/ota/vela_IPC_DB.bin of=/dev/IPC_DB bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_IPC_DB.bin failed"
    exit
fi
setprop ota.progress.current 31
setprop ota.progress.next 35

echo "install vela_ap.bin"
time " dd if=/ota/vela_ap.bin of=/dev/ap bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_ap.bin failed"
    exit
fi
setprop ota.progress.current 35
setprop ota.progress.next 37

echo "install vela_ap_f.bin"
time " dd if=/ota/vela_ap_f.bin of=/dev/ap_f bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_ap_f.bin failed"
    exit
fi
setprop ota.progress.current 37
setprop ota.progress.next 52

echo "install vela_app.bin"
time " dd if=/ota/vela_app.bin of=/dev/app bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_app.bin failed"
    exit
fi
setprop ota.progress.current 52
setprop ota.progress.next 52

echo "generate vela_dl_nv_d.bin"
if [ $hw_id_flag -eq 1 ]
then
    echo "--------udp--------"
    time "xr_nv_update /ota/vela_dl_nv_d.bin"
else
    echo "--------c00--------"
    time "xr_nv_update /ota/vela_dl_nv_d.bin"
fi

if [ $? -ne 0 ]
then
    echo "update vela_dl_nv_d failed"
fi

setprop ota.progress.current 52
setprop ota.progress.next 52

echo "generate vela_dl_nv_d_bak.bin jump"

setprop ota.progress.current 52
setprop ota.progress.next 52

echo "install vela_dsp.bin"
time " dd if=/ota/vela_dsp.bin of=/dev/dsp bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_dsp.bin failed"
    exit
fi
setprop ota.progress.current 52
setprop ota.progress.next 52

echo "install vela_dsp_f.bin"
time " dd if=/ota/vela_dsp_f.bin of=/dev/dsp_f bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_dsp_f.bin failed"
    exit
fi
setprop ota.progress.current 52
setprop ota.progress.next 58

echo "install vela_font.bin"
time " dd if=/ota/vela_font.bin of=/dev/font bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_font.bin failed"
    exit
fi
setprop ota.progress.current 58
setprop ota.progress.next 58

echo "install vela_i18n.bin"
time " dd if=/ota/vela_i18n.bin of=/dev/i18n bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_i18n.bin failed"
    exit
fi
setprop ota.progress.current 58
setprop ota.progress.next 58

echo "install vela_mg_nv.bin"
if [ $hw_id_flag -eq 1 ]
then
    echo "--------udp--------"
    time " dd if=/ota/vela_mg_nv.bin of=/dev/mg_nv bs=32768"
else
    echo "--------c00--------"
    time " dd if=/ota/vela_mg_nv.bin of=/dev/mg_nv bs=32768"
fi

if [ $? -ne 0 ]
then
    echo "dd vela_mg_nv.bin failed"
fi
setprop ota.progress.current 58
setprop ota.progress.next 58

echo "install vela_mg_nv_1.bin"
if [ $hw_id_flag -eq 1 ]
then
    echo "--------udp jump--------"
else
    echo "--------c00--------"
    time " dd if=/ota/vela_mg_nv_1.bin of=/dev/mg_nv_1 bs=32768"
fi

if [ $? -ne 0 ]
then
    echo "dd vela_mg_nv_1.bin failed"
fi
setprop ota.progress.current 58
setprop ota.progress.next 60

echo "install vela_misc.bin"
time " dd if=/ota/vela_misc.bin of=/dev/misc bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_misc.bin failed"
    exit
fi
setprop ota.progress.current 60
setprop ota.progress.next 60

echo "install vela_mmap.bin"
time " dd if=/ota/vela_mmap.bin of=/dev/mmap bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_mmap.bin failed"
    exit
fi
setprop ota.progress.current 60
setprop ota.progress.next 62

echo "install vela_quickapp.bin"
time " dd if=/ota/vela_quickapp.bin of=/dev/quickapp bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_quickapp.bin failed"
    exit
fi
setprop ota.progress.current 62
setprop ota.progress.next 62

echo "install vela_sbl.bin"
time " dd if=/ota/vela_sbl.bin of=/dev/sbl bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_sbl.bin failed"
    exit
fi
setprop ota.progress.current 62
setprop ota.progress.next 62

echo "install vela_sbl_bak.bin"
time " dd if=/ota/vela_sbl_bak.bin of=/dev/sbl_bak bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_sbl_bak.bin failed"
    exit
fi
setprop ota.progress.current 62
setprop ota.progress.next 62

echo "install vela_sensor.bin"
time " dd if=/ota/vela_sensor.bin of=/dev/sensor bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_sensor.bin failed"
    exit
fi
setprop ota.progress.current 62
setprop ota.progress.next 62

echo "install vela_sensor_f.bin"
time " dd if=/ota/vela_sensor_f.bin of=/dev/sensor_f bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_sensor_f.bin failed"
    exit
fi
setprop ota.progress.current 62
setprop ota.progress.next 74

echo "install vela_system.bin"
time " dd if=/ota/vela_system.bin of=/dev/system bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_system.bin failed"
    exit
fi
setprop ota.progress.current 74
setprop ota.progress.next 74

echo "install vela_tee.bin"
time " dd if=/ota/vela_tee.bin of=/dev/tee bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_tee.bin failed"
    exit
fi
setprop ota.progress.current 74
setprop ota.progress.next 74

echo "install vela_tee_f.bin"
time " dd if=/ota/vela_tee_f.bin of=/dev/tee_f bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_tee_f.bin failed"
    exit
fi
setprop ota.progress.current 74
setprop ota.progress.next 77

echo "install vela_vendor.bin"
time " dd if=/ota/vela_vendor.bin of=/dev/vendor bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_vendor.bin failed"
    exit
fi
setprop ota.progress.current 77
setprop ota.progress.next 90

echo "install vela_watchface.bin"
time " dd if=/ota/vela_watchface.bin of=/dev/watchface bs=32768"
if [ $? -ne 0 ]
then
    echo "dd vela_watchface.bin failed"
    exit
fi
setprop ota.progress.current 90
