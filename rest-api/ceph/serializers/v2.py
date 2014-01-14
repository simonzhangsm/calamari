

from rest_framework import serializers


class ClusterSerializer(serializers.Serializer):
    class Meta:
        fields = ('update_time', 'id', 'name')

    update_time = serializers.DateTimeField()
    name = serializers.Field()
    id = serializers.Field()


class SyncObjectSerializer(serializers.Serializer):
    class Meta:
        fields = ('data',)

    data = serializers.Field()


class PoolSerializer(serializers.Serializer):
    class Meta:
        fields = ('name', 'id', 'size', 'pg_num', 'crush_ruleset', 'min_size', 'crash_replay_interval', 'crush_ruleset',
                  'pgp_num', 'hashpspool', 'full', 'quota_max_objects', 'quota_max_bytes')

    # Required in creation
    name = serializers.CharField(source='pool_name',
                                 help_text="Human readable name of the pool, may"
                                 "change over the pools lifetime at user request.")
    pg_num = serializers.IntegerField(
        help_text="Number of placement groups in this pool")

    # Not required in creation, immutable
    id = serializers.CharField(source='pool', required=False, help_text="Unique numeric ID")

    # May be set in creation or updates
    size = serializers.IntegerField(required=False,
                                    help_text="Replication factor")
    min_size = serializers.IntegerField(required=False,
                                        help_text="Minimum number of replicas required for I/O")
    crash_replay_interval = serializers.IntegerField(required=False,
                                                     help_text="Number of seconds to allow clients to "
                                                               "replay acknowledged, but uncommitted requests")
    crush_ruleset = serializers.IntegerField(required=False, help_text="CRUSH ruleset in use")
    # In 'ceph osd pool set' it's called pgp_num, but in 'ceph osd dump' it's called
    # pg_placement_num :-/
    pgp_num = serializers.IntegerField(source='pg_placement_num', required=False,
                                       help_text="Effective number of placement groups to use when calculating "
                                                 "data placement")

    # This is settable by 'ceph osd pool set' but in 'ceph osd dump' it only appears
    # within the 'flags' integer.  We synthesize a boolean from the flags.
    hashpspool = serializers.BooleanField(required=False, help_text="Enable HASHPSPOOL flag")

    # This is synthesized from ceph's 'flags' attribute, read only.
    full = serializers.BooleanField(required=False, help_text="True if the pool is full")

    quota_max_objects = serializers.IntegerField(required=False,
                                                 help_text="Quota limit on object count (0 is unlimited)")
    quota_max_bytes = serializers.IntegerField(required=False,
                                               help_text="Quota limit on usage in bytes (0 is unlimited)")


class CrushRuleSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'name', 'ruleset', 'type', 'min_size', 'max_size', 'steps')

    id = serializers.IntegerField(source='rule_id')
    name = serializers.CharField(source='rule_name')
    ruleset = serializers.IntegerField()
    type = serializers.IntegerField()
    min_size = serializers.IntegerField()
    max_size = serializers.IntegerField()
    steps = serializers.Field()


class CrushRuleSetSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'rules',)

    id = serializers.IntegerField()
    rules = CrushRuleSerializer(many=True)


class RequestSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'state', 'error')

    id = serializers.CharField()
    state = serializers.CharField()
    error = serializers.BooleanField()


class SaltKeySerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'status')

    id = serializers.CharField()
    status = serializers.CharField()


class ServiceSerializer(serializers.Serializer):
    class Meta:
        fields = ('fsid', 'type', 'id', 'running')

    fsid = serializers.SerializerMethodField("get_fsid")
    type = serializers.SerializerMethodField("get_type")
    id = serializers.SerializerMethodField("get_id")
    running = serializers.BooleanField()

    def get_fsid(self, obj):
        return obj['id'][0]

    def get_type(self, obj):
        return obj['id'][1]

    def get_id(self, obj):
        return obj['id'][2]


class SimpleServerSerializer(serializers.Serializer):
    class Meta:
        fields = ('fqdn', 'hostname', 'managed', 'last_contact', 'services')

    # Identifying information
    fqdn = serializers.CharField(help_text="Fully qualified domain name")
    hostname = serializers.CharField(help_text="Unqualified hostname")

    # Calamari monitoring status
    managed = serializers.BooleanField(
        help_text="True if this server is under Calamari server's control, false"
                  "if the server's existence was inferred via Ceph cluster maps.")
    last_contact = serializers.DateTimeField(
        help_text="The time at which this server last communicated with the Calamari"
                  "server.  This is always null for unmanaged servers")

    # Ceph usage
    services = ServiceSerializer(many=True, help_text="List of Ceph services seen"
                                 "on this server")


class ServerSerializer(SimpleServerSerializer):
    class Meta:
        fields = ('fqdn', 'hostname', 'services', 'frontend_addr', 'backend_addr',
                  'frontend_iface', 'backend_iface', 'managed', 'last_contact')

    # Ceph network configuration
    frontend_addr = serializers.CharField()  # may be null if no OSDs or mons on server
    backend_addr = serializers.CharField()  # may be null if no OSDs on server
    frontend_iface = serializers.CharField()  # may be null if interface for frontend addr not up
    backend_iface = serializers.CharField()  # may be null if interface for backend addr not up
