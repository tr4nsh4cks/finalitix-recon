import hudson.util.Secret

def secrets = [
  'CSDEV01-1_pass':    '{AQAAABAAAAAQu80z2+IB7HCyH6EqB7CyrqD/8L59GLuNixILnRADawE=}',
  'CSQAAPP01-1_pass':  '{AQAAABAAAAAQvCfrolDy/ZNokUSuHnrCLCvkuSvvyESOlJo+6Z48AsU=}',
  'CSQAAPP02-1_pass':  '{AQAAABAAAAAQyev4KTergPPsDf6Mo7tiaOBApz/lPrOCgAw6bhXbaB0=}',
  'CSQANGIN01-1_pass': '{AQAAABAAAAAQLA3k+0y8tIEG7CER1Qb/4GMKdft/K0Ffq0iB87nDzlA=}',
  'CSQAAMDIN02-1_pass':'{AQAAABAAAAAQYyrZCIEFX8tZldI9rnmmuTW0dGP31ZDwqN0gmMVb8LI=}',
  'CSQAAMDIN-2_pass':  '{AQAAABAAAAAQdh+MnHnNTeJMaVVjZ2RnzT5faU6Y/k5tR7LfvBF9POU=}',
  'CSQATASK01-1_pass': '{AQAAABAAAAAQnZN50DGRx8sMSnEPwLwmhPez3ZxNiNBA5KeoHDPxC1s=}',
  'CSQATASK02-3_pass': '{AQAAABAAAAAQZ9YJpmTRU0NfVCySy1Ucjg3eU4paQNaO5LoNyndhmS8=}',
  'CSQAAPP03-1_pass':  '{AQAAABAAAAAQb8UMijhFNc9zvtPMpo+Wl5ryaJOVm/L6n1Qqz5eE+pk=}',
  'CSQAAPP04-1_pass':  '{AQAAABAAAAAQqf5WMgNDJt9tVsyOGTBSkTzXASXxv5FbvYSfwVorrkU=}',
  'CSDEV02-2_pass':    '{AQAAABAAAAAQOhIvdp3WRg1x/HOctUYT0QoZdRIU3AUhn04k2fYnzPI=}',
  'CSDEV01-2_pass':    '{AQAAABAAAAAQ7K3Uu2VE7T77LzQyxgLReAiUqyyROlgpGpuXqTEixFQ=}',
  'X1DEVAPP01-2_pass': '{AQAAABAAAAAQigJIQun31+P9WRAHsAzvQudvv19wSzdkzh/dZSVPAyM=}',
  'CSDEV03-1_pass':    '{AQAAABAAAAAQuLSNBRbe6KWuM/etopypROYalJpOET+PDQEtdkOxdI8=}',
  'common_passphrase': '{AQAAABAAAAAQ42FNcrbem2jkp6cdmaA7BbEgy3MSw0NYIBn4Ss98g5M=}',
]

secrets.each { k, v ->
  try {
    def plain = Secret.fromString(v).getPlainText()
    println(k + '=' + (plain ?: '(empty)'))
  } catch (Exception e) {
    println(k + '=ERROR:' + e.message)
  }
}
