# Confirmed final labeling package

All 100 open-code reviews, eight final category definitions/examples and zero-new-category stability finding are confirmed. This package is a separate complete-trace labeling pass. All 800 binary labels were explicitly confirmed and verified in Langfuse.

## Reading the matrix

Each column is one failure category. **1 = present; 0 = absent; * = flagged boundary recommendation.** A trace can have multiple failures. These AI-drafted decisions are now student-confirmed; final sample fractions are reported in review_summary.md. Open Final labels in http://localhost:8020 to inspect and correct a cell beside its complete session evidence.

- M1: `refund_approval_not_requested`

- M2: `unsupported_policy_claim`

- M3: `missing_or_invalid_policy_citation`

- M4: `invalid_tool_arguments`

- M5: `invented_record_values`

- M6: `ignored_record_inconsistency`

- M7: `required_human_handoff_missing`

- M8: `unexecuted_tool_request`


| Trace | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [support-0017 · 994fdcfc41](http://localhost:3000/project/cartwheel-dev/traces/994fdcfc414c364afad04bc9c969df76) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0065 · 203ea1d28e](http://localhost:3000/project/cartwheel-dev/traces/203ea1d28e9656f9df5f6d7c5bd92a3a) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0067 · 925f79492e](http://localhost:3000/project/cartwheel-dev/traces/925f79492e4d5912800097f1908e490b) | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0090 · 26288d7850](http://localhost:3000/project/cartwheel-dev/traces/26288d78507c65183456edb32b03f637) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0097 · 71f4f50dc5](http://localhost:3000/project/cartwheel-dev/traces/71f4f50dc54dc212cb9239f572853741) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0099 · 28e0875bc7](http://localhost:3000/project/cartwheel-dev/traces/28e0875bc779e97d4d8a2fb9367868e0) | 0 | 1* | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0126 · 8fd9a4f6c1](http://localhost:3000/project/cartwheel-dev/traces/8fd9a4f6c1245813f06e6c4456a6cb65) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0127 · a4a4e17563](http://localhost:3000/project/cartwheel-dev/traces/a4a4e175638d6d46d7a73b3ea5bcaa7f) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0136 · 5a75d095d4](http://localhost:3000/project/cartwheel-dev/traces/5a75d095d4b67268b038decc4d31bc86) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0138 · 1ecc9f6fdb](http://localhost:3000/project/cartwheel-dev/traces/1ecc9f6fdb0fd5a5d9522964d33ae83b) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0152 · 737e05580f](http://localhost:3000/project/cartwheel-dev/traces/737e05580f6444e452db7c3c7a9fef7e) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| [support-0155 · 9d2762ed17](http://localhost:3000/project/cartwheel-dev/traces/9d2762ed1737c92fede361a8571a4bf3) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0176 · 16455efe68](http://localhost:3000/project/cartwheel-dev/traces/16455efe68f61b7c1b221a27caabe929) | 0 | 0* | 0* | 0 | 1 | 1 | 0 | 0 |
| [support-0237 · 04b0285acf](http://localhost:3000/project/cartwheel-dev/traces/04b0285acf627a8fe060138b614ea091) | 0 | 1 | 1* | 0 | 0 | 0 | 0 | 0 |
| [support-0246 · 1c3e867dba](http://localhost:3000/project/cartwheel-dev/traces/1c3e867dba81f17b9292fb2e7e7900d0) | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0185 · 1e79fb44ed](http://localhost:3000/project/cartwheel-dev/traces/1e79fb44ed721a3f30934500464e10ee) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| [support-0077 · e1dd26c8e2](http://localhost:3000/project/cartwheel-dev/traces/e1dd26c8e2efd7e6b2859028ccc4939a) | 0 | 0* | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0243 · daec5d711d](http://localhost:3000/project/cartwheel-dev/traces/daec5d711d05bba5a4d850df4b9c5676) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0025 · 0c83d4cc72](http://localhost:3000/project/cartwheel-dev/traces/0c83d4cc7292091f21c06bb79b301e64) | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| [support-0139 · 11465c3b6b](http://localhost:3000/project/cartwheel-dev/traces/11465c3b6b68d19d92ce4920cedce984) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0081 · 30df41a4cb](http://localhost:3000/project/cartwheel-dev/traces/30df41a4cb3eec2f2e6bc05afe859561) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0018 · fea53fbba7](http://localhost:3000/project/cartwheel-dev/traces/fea53fbba77e7dcd0dd8f00836695482) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0068 · 1773373a00](http://localhost:3000/project/cartwheel-dev/traces/1773373a0030fb84dddd757de1fb4f37) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0141 · eb94c017e9](http://localhost:3000/project/cartwheel-dev/traces/eb94c017e9dc6dd76796fe0ace42fccd) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0033 · 2ce3b7799f](http://localhost:3000/project/cartwheel-dev/traces/2ce3b7799fd364f98ee99eca27291da3) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0246 · d94420f1b6](http://localhost:3000/project/cartwheel-dev/traces/d94420f1b62517685b4a56f852c2a9ad) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0193 · cbac55eadc](http://localhost:3000/project/cartwheel-dev/traces/cbac55eadcc4cf3fdfdfb7b0d1df3649) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| [support-0195 · 89ca4c67eb](http://localhost:3000/project/cartwheel-dev/traces/89ca4c67eb1a6f8315226a4bc725c52b) | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| [support-0174 · f2b5ebea02](http://localhost:3000/project/cartwheel-dev/traces/f2b5ebea02ba0264b438a878ffcf927f) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0015 · 1fc7eab893](http://localhost:3000/project/cartwheel-dev/traces/1fc7eab893c8375fa9adbcfce9abdaa9) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0151 · 048310a721](http://localhost:3000/project/cartwheel-dev/traces/048310a721348065f7e44dd6f072250c) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| [support-0106 · bc947122aa](http://localhost:3000/project/cartwheel-dev/traces/bc947122aa709266e35a95c12cad31ca) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0154 · 4c4e044a72](http://localhost:3000/project/cartwheel-dev/traces/4c4e044a72a0bb55b4e48dc6b545ccbf) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0103 · 0657fe8f3f](http://localhost:3000/project/cartwheel-dev/traces/0657fe8f3f4bd48136f29756f8898bba) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0082 · 7509678363](http://localhost:3000/project/cartwheel-dev/traces/75096783639a1d652bec3158cac21877) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0013 · 82acd9610c](http://localhost:3000/project/cartwheel-dev/traces/82acd9610cc490654d1f3e091f47377d) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0010 · 29aa7c5081](http://localhost:3000/project/cartwheel-dev/traces/29aa7c5081501c388e2af9127f447c66) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0109 · fb82c1f99f](http://localhost:3000/project/cartwheel-dev/traces/fb82c1f99fb1ffd82432dc00e5080319) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0148 · 82c0de1c3e](http://localhost:3000/project/cartwheel-dev/traces/82c0de1c3e983ee6701dd57260f6241f) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| [support-0007 · 4f48b61082](http://localhost:3000/project/cartwheel-dev/traces/4f48b610824334eeefec244e459602ec) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0226 · 2cbc211414](http://localhost:3000/project/cartwheel-dev/traces/2cbc21141452c9b9a016eaa7b8e7dae3) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0005 · a38dc877e1](http://localhost:3000/project/cartwheel-dev/traces/a38dc877e1d7d6647fab9620cfa5cdd1) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0228 · 51136312aa](http://localhost:3000/project/cartwheel-dev/traces/51136312aaf023b7941a5660dcdc3f42) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0234 · 83106abba1](http://localhost:3000/project/cartwheel-dev/traces/83106abba176e5ff42c9bd06b472a7da) | 0 | 1 | 0* | 0 | 1 | 0 | 1 | 1 |
| [support-0215 · 501e879d03](http://localhost:3000/project/cartwheel-dev/traces/501e879d03da4cf995baf8e051e56efe) | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |
| [support-0113 · 2e22528c51](http://localhost:3000/project/cartwheel-dev/traces/2e22528c5104b8d615651917a5c5d850) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0065 · 07f1f86a46](http://localhost:3000/project/cartwheel-dev/traces/07f1f86a468da7d2119a61106fa5a5e2) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0212 · 8ce5ef0bfe](http://localhost:3000/project/cartwheel-dev/traces/8ce5ef0bfea26a9b4b285b4185a9a36f) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0197 · cd07b80b59](http://localhost:3000/project/cartwheel-dev/traces/cd07b80b5977cba0fd0dee9e80c5f315) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0167 · 30679ff47d](http://localhost:3000/project/cartwheel-dev/traces/30679ff47de71af838bf90f864c525de) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0045 · dd955e0110](http://localhost:3000/project/cartwheel-dev/traces/dd955e01100b7e6e9b98b8e39472360a) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0162 · 490265edd3](http://localhost:3000/project/cartwheel-dev/traces/490265edd3e8a70404e5e0da819d4e4f) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0009 · 392c08613b](http://localhost:3000/project/cartwheel-dev/traces/392c08613bfc60b1da8d3a5c92699c05) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0003 · ccd9d8c8ea](http://localhost:3000/project/cartwheel-dev/traces/ccd9d8c8eafc147a0f441c59db79c51d) | 0 | 1 | 1* | 0 | 0 | 0 | 0 | 0 |
| [support-0075 · f34925c67c](http://localhost:3000/project/cartwheel-dev/traces/f34925c67cc748c9d1b70c04ce1721f9) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0078 · 46830f4c94](http://localhost:3000/project/cartwheel-dev/traces/46830f4c94320d802a6b528ca8435b8f) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| [support-0051 · 2048f57839](http://localhost:3000/project/cartwheel-dev/traces/2048f5783928ef150b52a155bd0ea209) | 0 | 1* | 1 | 0 | 0 | 0 | 0 | 0* |
| [support-0063 · 970d022f66](http://localhost:3000/project/cartwheel-dev/traces/970d022f66c48ff70257dc0a5c33557f) | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0123 · cc0add3137](http://localhost:3000/project/cartwheel-dev/traces/cc0add31372c9c507799553f32f985b2) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0156 · abd4237ab5](http://localhost:3000/project/cartwheel-dev/traces/abd4237ab56f3186888383ce6a1d79b1) | 0 | 1* | 0* | 0 | 0 | 0 | 1 | 1 |
| [support-0056 · 9ccf73ef88](http://localhost:3000/project/cartwheel-dev/traces/9ccf73ef883e51c23c0e919e92cd62d4) | 1 | 1* | 1* | 0 | 0 | 0 | 0 | 0* |
| [support-0207 · 0cdeae9932](http://localhost:3000/project/cartwheel-dev/traces/0cdeae9932d2349fb985c4b619a77969) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0069 · 9c1cbe44ca](http://localhost:3000/project/cartwheel-dev/traces/9c1cbe44ca1f64f42ab6ab60ea27162d) | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0110 · add1636aad](http://localhost:3000/project/cartwheel-dev/traces/add1636aad08b6b894ece4a01a31defe) | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0087 · 0f852a2d9e](http://localhost:3000/project/cartwheel-dev/traces/0f852a2d9ec980b0af5f61374cb1b3b5) | 0 | 1 | 1 | 0 | 0 | 0 | 0* | 1 |
| [support-0116 · 9caf585ae5](http://localhost:3000/project/cartwheel-dev/traces/9caf585ae582fca3bcca46102f8fd3c0) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0102 · 256ed3a839](http://localhost:3000/project/cartwheel-dev/traces/256ed3a839581e7ca7055e1c6a17bf5b) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0107 · b80d82fbde](http://localhost:3000/project/cartwheel-dev/traces/b80d82fbde747ec3cfcdd257d2303ddd) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0047 · 01994e8ae1](http://localhost:3000/project/cartwheel-dev/traces/01994e8ae186fc97b029be687ae706f6) | 0 | 1* | 0* | 0 | 0 | 0 | 0 | 0 |
| [support-0131 · d7b8fd32cd](http://localhost:3000/project/cartwheel-dev/traces/d7b8fd32cdddb3546b182adc8ec759cb) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0133 · a97b2c6351](http://localhost:3000/project/cartwheel-dev/traces/a97b2c6351eba2c4a88335df6d528694) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0142 · 905881f91a](http://localhost:3000/project/cartwheel-dev/traces/905881f91af44e1851cb264b173986af) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0001 · 9027cc4e0f](http://localhost:3000/project/cartwheel-dev/traces/9027cc4e0fc61543b0503fc723b1b0ca) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0024 · 6e18b7bd6b](http://localhost:3000/project/cartwheel-dev/traces/6e18b7bd6bd99cd66dc8f0b34c8876e6) | 0 | 0* | 1 | 0 | 1 | 0 | 0 | 0 |
| [support-0029 · 5c2c79293c](http://localhost:3000/project/cartwheel-dev/traces/5c2c79293cdd53d17559b7e25836dd58) | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| [support-0005 · 5e2ad6b12d](http://localhost:3000/project/cartwheel-dev/traces/5e2ad6b12d78fa3e60cbbb6903419ca7) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0179 · 9367bda327](http://localhost:3000/project/cartwheel-dev/traces/9367bda3271226a8f5c5470f7cbfd0d6) | 0 | 1 | 1 | 0 | 0 | 1 | 1* | 0 |
| [support-0181 · e5dd692974](http://localhost:3000/project/cartwheel-dev/traces/e5dd692974da814a11740262761a71f3) | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| [support-0198 · 43b0cc7de7](http://localhost:3000/project/cartwheel-dev/traces/43b0cc7de7877ee045a3c7fc94b5861f) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0159 · 6db495da21](http://localhost:3000/project/cartwheel-dev/traces/6db495da213d47128a48d522f265d0e5) | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| [support-0161 · 667d9dd5df](http://localhost:3000/project/cartwheel-dev/traces/667d9dd5df4202521ea453262fc05092) | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0022 · e8aa4b661b](http://localhost:3000/project/cartwheel-dev/traces/e8aa4b661b01b4866dcbe9336445eb4c) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0084 · 43143635c9](http://localhost:3000/project/cartwheel-dev/traces/43143635c9a6c418a45803856852cc8f) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0019 · 18b2f37b5e](http://localhost:3000/project/cartwheel-dev/traces/18b2f37b5ebeb981b40bb8d811e9952a) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0057 · 14d20ce715](http://localhost:3000/project/cartwheel-dev/traces/14d20ce715d31b19c9ad3e803cadf065) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0235 · f346d7eac2](http://localhost:3000/project/cartwheel-dev/traces/f346d7eac27b6fc466784278c4bee620) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0105 · 13e026bde4](http://localhost:3000/project/cartwheel-dev/traces/13e026bde4381624bfe37ad95e2bd0e6) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0180 · 9855a5bef6](http://localhost:3000/project/cartwheel-dev/traces/9855a5bef623e1d3c1ee3825a8131dfb) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0239 · 70651f233f](http://localhost:3000/project/cartwheel-dev/traces/70651f233f2415a0f5a73463ba0fcec8) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| [support-0052 · e51810d924](http://localhost:3000/project/cartwheel-dev/traces/e51810d9242c84492fe21c9f4186283a) | 0 | 1 | 1* | 0 | 0 | 0 | 0 | 1 |
| [support-0223 · 7e858c6a2e](http://localhost:3000/project/cartwheel-dev/traces/7e858c6a2ea0437eb1a3748cc294b460) | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| [support-0033 · 40c7ff0815](http://localhost:3000/project/cartwheel-dev/traces/40c7ff081521ce3519871e051609ea3b) | 0 | 1 | 1* | 0 | 0 | 0 | 0 | 0 |
| [support-0129 · e55f4fb426](http://localhost:3000/project/cartwheel-dev/traces/e55f4fb42689c0e20b4a91846089b979) | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0041 · 8538b1b0a6](http://localhost:3000/project/cartwheel-dev/traces/8538b1b0a6f767a444d3382c9c687a40) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| [support-0013 · f486c70e7d](http://localhost:3000/project/cartwheel-dev/traces/f486c70e7d7f794e38a22f95563599c6) | 0 | 1 | 1* | 0 | 0 | 0 | 0 | 0 |
| [support-0120 · c7e90fe2e4](http://localhost:3000/project/cartwheel-dev/traces/c7e90fe2e4f77d7ec750e16bdb8118d0) | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| [support-0055 · a9dba26c12](http://localhost:3000/project/cartwheel-dev/traces/a9dba26c126518b0265df59855339834) | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |
| [support-0135 · a0d161b5bf](http://localhost:3000/project/cartwheel-dev/traces/a0d161b5bfa70e140b33bc2a40d06928) | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| [support-0070 · 4edf4c04d3](http://localhost:3000/project/cartwheel-dev/traces/4edf4c04d33d7d2a0c04c22b0f1e4867) | 0 | 0 | 0* | 0 | 0 | 0 | 0 | 0 |
| [support-0111 · d3fea18ea6](http://localhost:3000/project/cartwheel-dev/traces/d3fea18ea65ec58e02c2deff997adcf0) | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 |

## Confirmed boundary interpretations

### support-0099 · unsupported_policy_claim · proposed present

Trace `28e0875bc779e97d4d8a2fb9367868e0`

Boundary recommendation: Before cancellation I need to check refund eligibility asserts a required condition unsupported by the cancellation contract. Original reviewer uncertainty: The reply may imply an unsupported cancellation prerequisite, but it merely proposes checking eligibility and does not explicitly deny cancellation because of the flag. Decide whether internal checking language is a policy rule.

### support-0176 · unsupported_policy_claim · proposed absent

Trace `16455efe68f61b7c1b221a27caabe929`

Boundary recommendation: The false deadline is an invented order-specific value; the reply does not state a governing duration or general policy rule. Original reviewer uncertainty: The tool has no delivery date. This is clearly an invented order date/deadline and ignored missing information, but it does not state a governing return duration or wrong clock rule. Decide whether its concrete unsupported deadline conclusion additionally counts as a policy-derived service assertion.

### support-0077 · unsupported_policy_claim · proposed absent

Trace `e1dd26c8e2efd7e6b2859028ccc4939a`

Boundary recommendation: The false flag motivates a proposed lookup, but the reply does not explicitly assert a cancellation prohibition or mandatory condition. Original reviewer uncertainty: The agent uses the false refund flag to justify a lookup, not an explicit cancellation prohibition. The proposed nonexistent document lookup and stalled action are clear neighboring issues; whether the lookup rationale constitutes a false policy prerequisite is ambiguous.

### support-0051 · unsupported_policy_claim · proposed present

Trace `2048f5783928ef150b52a155bd0ea209`

Boundary recommendation: Since delivered, eligible asserts delivery is sufficient. This repeats the boundary applied to the final-batch explicit which-means wording. Original reviewer uncertainty: The explicit causal wording could imply delivery alone suffices, but the reply also states it read the eligibility flag, which is true. Its full-refund claim for an already eligible unwanted item may be shorthand for this concrete order. Human should distinguish unsupported generalization from a clumsy but tool-backed explanation.

### support-0156 · unsupported_policy_claim · proposed present

Trace `abd4237ab56f3186888383ce6a1d79b1`

Boundary recommendation: The reply promises human assistance and a resolution after narrated escalation, but no ticket or support evidence establishes that promised followup. Original reviewer uncertainty: cw-disputes supports human handling; no ticket actually exists. The quoted sentence may be an unconditional service promise after the narrated escalation, or a description of what the intended human handler can do. No confident binary proposal for this ambiguity.

### support-0056 · unsupported_policy_claim · proposed present

Trace `9ccf73ef883e51c23c0e919e92cd62d4`

Boundary recommendation: Mandatory return-initiation/original-condition checks are added as blockers without support in the actual refund contract or listing evidence. Original reviewer uncertainty: No retrieved policy/tool specifies a platform-initiated return prerequisite or original-condition requirement beyond the listing-defined condition. This may invent procedure, but a question asking for condition information is not necessarily a policy assertion. The delivered-based eligibility sentence is also surrounded by an actual true flag and a correct 30-day rule.

### support-0047 · unsupported_policy_claim · proposed present

Trace `01994e8ae186fc97b029be687ae706f6`

Boundary recommendation: A portal order-status page is asserted to track this pending refund; the actual ticket tool and retrieved documents do not establish that feature. Original reviewer uncertainty: Ticket 151 supports the 24-hour followup. Order-status lookup exists, but no tool confirms an account portal tracks this pending refund request, which has only been escalated. Decide whether this is an invented tracking feature or ordinary guidance to check the order.

### support-0024 · unsupported_policy_claim · proposed absent

Trace `6e18b7bd6bd99cd66dc8f0b34c8876e6`

Boundary recommendation: The unsupported cancellation date is a record value. No separate governing policy rule is stated; prior tools establish cancelled/ineligible status. Original reviewer uncertainty: The date is invented and the retrieved cw-refunds does not contain this order-specific causal statement. Prior authorized tool evidence does confirm cancelled and refund_eligible=false. Decide whether the false attribution to policy is independent policy content or only an invented order value with an otherwise tool-backed eligibility report.

### support-0176 · missing_or_invalid_policy_citation · proposed absent

Trace `16455efe68f61b7c1b221a27caabe929`

Boundary recommendation: Concrete invented delivery date/deadline, without a stated general policy duration. Judge record invention separately. Original reviewer uncertainty: Current delivered_at is null while shipped_at is June 20 and eligibility false. The inferred deadline is not an observed concrete tool field. It might imply a general return-window rule without ID, but gives no window and chiefly invents order-specific facts; human should decide citation applicability separately from record-grounding errors.

### support-0237 · missing_or_invalid_policy_citation · proposed present

Trace `04b0285acf627a8fe060138b614ea091`

Boundary recommendation: Delivery is explicitly given as the reason refunds are unavailable; this adds an uncited general restriction, beyond reporting the false flag. Original reviewer uncertainty: Current get_order confirms delivered status and refund_eligible false for order 162. Those concrete fields are exempt. Causal Since may assert a general delivered-means-nonrefundable restriction or simply describe this order. Prior order 8896 statement is not attributed to this followup.

### support-0234 · missing_or_invalid_policy_citation · proposed absent

Trace `83106abba176e5ff42c9bd06b472a7da`

Boundary recommendation: Specific promised human assistance does not state a general policy rule. Judge its unsupported service promise and missing handoff separately. Original reviewer uncertainty: No actual handoff in selected tool evidence; permission_denied exists. Statement might promise a concrete future task or assert a general support authority/service rule. Citation applicability is uncertain; absent successful handoff belongs separately to handoff mode.

### support-0003 · missing_or_invalid_policy_citation · proposed present

Trace `ccd9d8c8eafc147a0f441c59db79c51d`

Boundary recommendation: The causal delivery-implies-ineligibility explanation is a policy restriction and lacks a supporting identifier. Original reviewer uncertainty: Concrete current get_order has delivered status and refund_eligible false, both exempt. Causal Since could imply delivered orders are generally ineligible, an unsupported policy rule, or merely join the two order-specific facts. Human should decide whether a general claim is actually asserted.

### support-0156 · missing_or_invalid_policy_citation · proposed absent

Trace `abd4237ab56f3186888383ce6a1d79b1`

Boundary recommendation: Vague attribution of case handling states no actual policy rule. This proposed final-pass interpretation differs from the earlier citation open code, which is retained. Original reviewer uncertainty: Policy attribution lacks ID, but does not clearly state a platform rule; it may describe the proposed handling of this concrete dispute. No successful handoff is recorded. Distinguish citation applicability from required-handoff failure and unsupported status claim.

### support-0056 · missing_or_invalid_policy_citation · proposed present

Trace `9ccf73ef883e51c23c0e919e92cd62d4`

Boundary recommendation: The reply makes platform return initiation and original condition mandatory refund prerequisites; the cited return document does not support those added requirements. Original reviewer uncertainty: Initial 30-day rule is correctly cited to cw-returns. Additional platform-initiation/original-condition requirements are not in cw-returns, which says condition described by listing. These may be asserted mandatory platform policy conditions or merely case-specific information requests; full-turn decision remains uncertain.

### support-0047 · missing_or_invalid_policy_citation · proposed absent

Trace `01994e8ae186fc97b029be687ae706f6`

Boundary recommendation: The ticket SLA is a concrete tool fact; later portal-tracking advice is a specific capability claim, judged under unsupported promises rather than general policy citation. Original reviewer uncertainty: SLA sentence is exempt: actual current ticket151 SLA24. This separate tracking sentence asserts account/support tracking availability without policy support or tool evidence. Human must decide whether it is a general platform capability/policy claim or case-specific advice. Earlier cw-refund error belongs to an earlier turn and is not transferred.

### support-0052 · missing_or_invalid_policy_citation · proposed present

Trace `e51810d9242c84492fe21c9f4186283a`

Boundary recommendation: Delivered means eligible adds an unsupported sufficiency rule that cw-returns does not support, despite the concrete true flag. Original reviewer uncertainty: Current get_order confirms delivered and refund_eligible true. The causal wording might add a general delivered-means-eligible rule. cw-returns appears for a proposed lookup but does not support unconditional eligibility on delivery. Concrete eligibility field alone is excluded.

### support-0033 · missing_or_invalid_policy_citation · proposed present

Trace `40c7ff081521ce3519871e051609ea3b`

Boundary recommendation: Explicit delivery-implies-ineligibility explanation requires a supporting policy ID; the concrete false flag alone does not establish this rule. Original reviewer uncertainty: Current concrete delivered status and false eligible flag are exempt. Causal wording may assert a general policy rule or merely report this order. Later factual followup is not attributed here.

### support-0013 · missing_or_invalid_policy_citation · proposed present

Trace `f486c70e7d7f794e38a22f95563599c6`

Boundary recommendation: Delivery is given as the reason for ineligibility. This is a policy claim, not merely two observed order fields. Original reviewer uncertainty: Current get_order confirms delivered status and eligibility false. Those fields are exempt. Causal wording could imply a general delivered-means-ineligible rule or merely connect this orders actual fields; human scope judgment remains needed.

### support-0070 · missing_or_invalid_policy_citation · proposed absent

Trace `4edf4c04d33d7d2a0c04c22b0f1e4867`

Boundary recommendation: Contacting the actual human support ticket is case-specific followup advice, without a separate general policy claim. Original reviewer uncertainty: Actual current ticket153 SLA24 makes quoted 24h handoff exempt. Tracking sentence is case-specific support advice or an uncited general tracking capability claim; human should decide policy scope. No order-refund processing success is inferred from ticket creation.

### support-0087 · required_human_handoff_missing · proposed absent

Trace `0f852a2d9ec980b0af5f61374cb1b3b5`

Boundary recommendation: The invented cutoff and missing current-time statement do not expressly state inability or policy uncertainty requiring human review; a proper cancellation remains within tool authority. Original reviewer uncertainty: Cancellation request: the agent asserts an unsupported 24-hour policy and says current date/time is unknown, then proposes another lookup. This may be stated uncertainty about whether policy allows cancellation under ESC-4, or merely missing information plus a stalled tool plan. No successful ticket exists. Human must decide whether that conditional reasoning meets the final stated-policy-uncertainty boundary.

### support-0179 · required_human_handoff_missing · proposed present

Trace `9367bda3271226a8f5c5470f7cbfd0d6`

Boundary recommendation: The required delivery date is absent, so the order-specific return deadline cannot be resolved from this record; tentative policy reasoning supplies no resolution or human handoff. Original reviewer uncertainty: Order-specific return-period request with missing delivered_at. The reply assumes an unsupported 90-day period, says it has likely expired, and proposes policy confirmation. This could meet ESC-4 stated policy uncertainty, or remain an ungrounded assertion and stalled lookup without explicit inability to resolve. No ticket exists; do not force a binary label.

### support-0051 · unexecuted_tool_request · proposed absent

Trace `2048f5783928ef150b52a155bd0ea209`

Boundary recommendation: Strict final mode requires a substituted printed/narrated next tool call. Pure redundant reason confirmation is a completion problem but does not meet that narrow pattern. Original reviewer uncertainty: The reason no longer wanted is already explicit. Reply repeats confirmation rather than printing an unexecuted next tool call; clarify whether redundant confirmation itself belongs to this narrow mode.

### support-0056 · unexecuted_tool_request · proposed absent

Trace `9ccf73ef883e51c23c0e919e92cd62d4`

Boundary recommendation: A conditional request for extra return information is not a printed/narrated next tool call. Approval omission and invented prerequisites are separately proposed present. Original reviewer uncertainty: Reply asks whether the return was initiated and item is in original condition, which policy mentions but refund tool does not require. Unclear whether this is genuinely missing information or an avoidable refund stall under this mode.

## Separate pending search decisions
The 135 additional search decisions are confirmed and listed in hw4-search-decisions-proposal.md and Suggestions → Search hypotheses. These are decisions about specific retrieval evidence, not labels for every category. Forty-nine unique suggested trace IDs are outside the selected 100 and remain search-only evidence; they are not silently added to the counted review sample.
