Possible schema?

Tables:
    hosts
        id
        hostname
        last_seen

    disks
        id
        hosts_id
        device_number           (str) # 9:9
        device_name             (str) # sda1
        device_type             (enum) # partition | disk
        partition_of            (str) # sda
        partition_number        (tinyint) # 1
        model                   (str) # TOSHIBA HDWG180
        serial                  (str) # 2K492LAGCGDP
        firmware                (str) # 32B3T8EA
        time_gathered

    disks_iostats
        id
        disks_id
        in_flight               # 0
        read_ios                # 6130275
        read_merge              # 658999
        read_sectors            # 191645067
        read_ticks              # 1116222
        total_io_ticks          # 390952
        total_time_in_queue     # 854248
        write_ios               # 9844858
        write_merges            # 1776543
        write_sectors           # 837801345
        write_ticks             # 1295690
        time_gathered

    filesystems
        id
        hosts_id
        disks_id
        mount_point             (str) # /
        device                  (str) # zpool1/zfs530/zfs5300001/36956a13301194aa05f5a85665480f1d64f776e6e7e1ee11e99a076665c9c017
        filesystem              (str) # ZFS
        pass                    (int) # 0
        dump                    (int) # 0
        bytes_available         (int) # 7187865354240
        bytesFree               (int) # 7187865354240
        bytesTotal              (int) # 7188274192384
        f_bavail                (int) # 14038799520
        f_bfree                 (int) # 14038799520
        f_blocks                (int) # 14039598032
        f_bsize                 (int) # 512
        f_favail                (int) # 14038799520
        f_ffree                 (int) # 14038799520
        f_files                 (int) # 14038817355
        f_flag                  (int) # 4096
        f_frsize                (int) # 512
        f_namemax               (int) # 255
        pct_available           (float) # 99.99431242975632
        pct_free                (float) # 99.99431242975632
        pct_reserved            (float) # 0.005687570243673168
        pct_used                (float) # 0.005687570243673168
        time_gathered

    filesystems_mount_options
        id
        filesystems_id
        option
        value

    filesystems_performance
        id
        filesystems_id

    memory
        active                  (int) # 2202644480
        active_anon             (int) # 1977335808
        active_file             (int) # 225308672
        anon_pages              (int) # 2073997312
        bounce                  (int) # 0
        buffers                 (int) # 27754496
        cached                  (int) # 883712000
        commit_limit            (int) # 84249346048
        committed_as            (int) # 18924425216
        direct_map_1g           (int) # 1073741824
        direct_map_2m           (int) # 23444062208
        direct_map4k            (int) # 9730924544
        dirty                   (int) # 69632
        hardware_corrupted      (int) # 0
        hugepages_free          (int) # 0
        hugepages_rsvd          (int) # 0
        hugepages_surp          (int) # 0
        hugepages_total         (int) # 0
        hugepagesize            (int) # 2097152
        inactive                (int) # 854904832
        inactive_anon           (int) # 632946688
        inactive_file           (int) # 221958144
        kernel_stack            (int) # 73121792
        mapped                  (int) # 404729856
        mem_available           (int) # 8883154944
        mem_free                (int) # 8907005952
        mem_total               (int) # 33637154816
        mlocked                 (int) # 16187392
        nfs_unstable            (int) # 0
        page_tables             (int) # 84652032
        sreclaimable            (int) # 73445376
        sunreclaim              (int) # 13346287616
        shmem                   (int) # 507121664
        slab                    (int) # 13419732992
        swap_cached             (int) # 187019264
        swap_free               (int) # 66354667520
        swap_total              (int) # 67430768640
        unevictable             (int) # 16187392
        vmalloc_chunk           (int) # 0
        vmalloc_total           (int) # 35184372087808
        vmalloc_used            (int) # 0
        writeback               (int) # 0
        writeback_tmp           (int) # 0
        time_gathered           (float) # 1627376654.5297608

    cpu_specifications

    cpu_performance

    alarms
