import pandas as pd
from audittrail import AuditTrail

df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
audit = AuditTrail()
audit.take_snapshot(df, name='initial')
audit.describe_snapshot('initial')
