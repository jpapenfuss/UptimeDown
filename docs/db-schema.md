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

    memory_vmstats  # The number of entries in this vary wildly between an ec2
                    # instance and my dl325, with the instance having like 75 more entries.
        allocstall_dma				        # 0
        allocstall_dma32				    # 0
        allocstall_movable				    # 20
        allocstall_normal				    # 2
        balloon_deflate				        # 0
        balloon_inflate				        # 0
        balloon_migrate				        # 0
        compact_daemon_free_scanned			# 122075
        compact_daemon_migrate_scanned		# 4697
        compact_daemon_wake				    # 3
        compact_fail				        # 29
        compact_free_scanned				# 1853968
        compact_isolated				    # 112074
        compact_migrate_scanned				# 103679
        compact_stall				        # 102
        compact_success				        # 73
        drop_pagecache				        # 0
        drop_slab				            # 0
        htlb_buddy_alloc_fail				# 0
        htlb_buddy_alloc_success			# 0
        kswapd_high_wmark_hit_quickly		# 143
        kswapd_inodesteal				    # 379626
        kswapd_low_wmark_hit_quickly		# 142
        nr_active_anon				        # 138169
        nr_active_file				        # 116369
        nr_anon_pages				        # 140930
        nr_anon_transparent_hugepages		# 0
        nr_bounce				            # 0
        nr_dirtied				            # 8990920
        nr_dirty				            # 27
        nr_dirty_background_threshold		# 27501
        nr_dirty_threshold				    # 55070
        nr_file_hugepages				    # 0
        nr_file_pages				        # 227769
        nr_file_pmdmapped				    # 0
        nr_foll_pin_acquired				# 0
        nr_foll_pin_released				# 0
        nr_free_cma				            # 0
        nr_free_pages				        # 68993
        nr_inactive_anon				    # 29
        nr_inactive_file				    # 108877
        nr_isolated_anon				    # 0
        nr_isolated_file				    # 0
        nr_kernel_misc_reclaimable	        # 0
        nr_kernel_stack				        # 4160
        nr_mapped				            # 42914
        nr_mlock				            # 4616
        nr_page_table_pages				    # 2250
        nr_shmem				            # 209
        nr_shmem_hugepages				    # 0
        nr_shmem_pmdmapped				    # 0
        nr_slab_reclaimable				    # 33535
        nr_slab_unreclaimable				# 16285
        nr_unevictable				        # 5750
        nr_unstable				            # 0
        nr_vmscan_immediate_reclaim		    # 2845
        nr_vmscan_write				        # 0
        nr_writeback				        # 0
        nr_writeback_temp				    # 0
        nr_written				            # 8057661
        nr_zone_active_anon				    # 138169
        nr_zone_active_file				    # 116369
        nr_zone_inactive_anon				# 29
        nr_zone_inactive_file				# 108877
        nr_zone_unevictable				    # 5750
        nr_zone_write_pending				# 28
        nr_zspages				            # 0
        numa_foreign				        # 0
        numa_hint_faults				    # 0
        numa_hint_faults_local				# 0
        numa_hit				            # 652696815
        numa_huge_pte_updates				# 0
        numa_interleave				        # 3604
        numa_local				            # 652696815
        numa_miss				            # 0
        numa_other				            # 0
        numa_pages_migrated				    # 0
        numa_pte_updates				    # 0
        oom_kill				            # 0
        pageoutrun				            # 542
        pgactivate				            # 2579597
        pgalloc_dma				            # 118302
        pgalloc_dma32				        # 658832442
        pgalloc_movable				        # 0
        pgalloc_normal				        # 0
        pgdeactivate				        # 1431936
        pgfault				                # 671283144
        pgfree				                # 659077073
        pginodesteal				        # 0
        pglazyfree				            # 39116139
        pglazyfreed				            # 7838
        pgmajfault				            # 21703
        pgmigrate_fail				        # 17
        pgmigrate_success				    # 53065
        pgpgin				                # 5129582
        pgpgout				                # 35745224
        pgrefill				            # 1609129
        pgrotated				            # 4934
        pgscan_anon				            # 0
        pgscan_direct				        # 5964
        pgscan_direct_throttle				# 0
        pgscan_file				            # 2019420
        pgscan_kswapd				        # 2013456
        pgskip_dma				            # 0
        pgskip_dma32				        # 0
        pgskip_movable				        # 0
        pgskip_normal				        # 0
        pgsteal_anon				        # 0
        pgsteal_direct				        # 5834
        pgsteal_file				        # 1863718
        pgsteal_kswapd				        # 1857884
        pswpin				                # 0
        pswpout				                # 0
        slabs_scanned				        # 1881804
        swap_ra				                # 0
        swap_ra_hit				            # 0
        thp_collapse_alloc				    # 2944
        thp_collapse_alloc_failed		    # 5
        thp_deferred_split_page				# 540
        thp_fault_alloc				        # 32
        thp_fault_fallback				    # 0
        thp_fault_fallback_charge			# 0
        thp_file_alloc				        # 0
        thp_file_fallback				    # 0
        thp_file_fallback_charge			# 0
        thp_file_mapped				        # 0
        thp_split_page				        # 531
        thp_split_page_failed				# 0
        thp_split_pmd				        # 540
        thp_split_pud				        # 0
        thp_swpout				            # 0
        thp_swpout_fallback				    # 0
        thp_zero_page_alloc				    # 0
        thp_zero_page_alloc_failed			# 0
        unevictable_pgs_cleared				# 53
        unevictable_pgs_culled				# 9262
        unevictable_pgs_mlocked				# 8181
        unevictable_pgs_munlocked			# 3512
        unevictable_pgs_rescued				# 3512
        unevictable_pgs_scanned				# 0
        unevictable_pgs_stranded			# 53
        workingset_activate				    # 284301
        workingset_nodereclaim				# 31573
        workingset_nodes				    # 1669
        workingset_refault				    # 491325
        workingset_restore				    # 202801
        zone_reclaim_failed				    # 0
        time_gathered

    cpu_specifications

    cpu_performance

    alarms
