# Changelog

## [0.6.1](https://github.com/ansys/pyturbogrid/compare/v0.6.0...v0.6.1) (2026-04-30)


### Build System

* **deps:** Bump autodocsumm from 0.2.14 to 0.2.15 ([#374](https://github.com/ansys/pyturbogrid/issues/374)) ([78af23e](https://github.com/ansys/pyturbogrid/commit/78af23ecab2af464a3da91404dbd8212b990e25b))
* **deps:** Bump deepdiff from 8.6.2 to 9.0.0 ([#385](https://github.com/ansys/pyturbogrid/issues/385)) ([f9f6448](https://github.com/ansys/pyturbogrid/commit/f9f6448b0e7a3e3d59cf211fc5aa584136adfa83))
* **deps:** Bump fabric from 3.2.2 to 3.2.3 ([#388](https://github.com/ansys/pyturbogrid/issues/388)) ([01736b6](https://github.com/ansys/pyturbogrid/commit/01736b69f4dcf2a884ec8c4414b5bf8eb8f7a263))
* **deps:** Bump importlib-metadata from 8.7.1 to 9.0.0 ([#371](https://github.com/ansys/pyturbogrid/issues/371)) ([c41e081](https://github.com/ansys/pyturbogrid/commit/c41e08171f0d7605c884e146102b10896139e20b))
* **deps:** Bump matplotlib from 3.10.8 to 3.10.9 ([#387](https://github.com/ansys/pyturbogrid/issues/387)) ([eeb974c](https://github.com/ansys/pyturbogrid/commit/eeb974ce5d0ddcbc5756121cf1b09dc862f2e3a6))
* **deps:** Bump nbconvert from 7.17.0 to 7.17.1 ([#378](https://github.com/ansys/pyturbogrid/issues/378)) ([4045241](https://github.com/ansys/pyturbogrid/commit/40452416823bca4b168d62d996abe60aacf3df30))
* **deps:** Bump notebook from 7.5.4 to 7.5.5 ([#368](https://github.com/ansys/pyturbogrid/issues/368)) ([2658cce](https://github.com/ansys/pyturbogrid/commit/2658cce0e3a5f06d4aa2bdd227137843dea97b49))
* **deps:** Bump notebook from 7.5.5 to 7.5.6 ([#390](https://github.com/ansys/pyturbogrid/issues/390)) ([d9c93ac](https://github.com/ansys/pyturbogrid/commit/d9c93ac3f2c035208959ada251994dfcddd3d93e))
* **deps:** Bump pytest from 9.0.2 to 9.0.3 ([#389](https://github.com/ansys/pyturbogrid/issues/389)) ([c5be059](https://github.com/ansys/pyturbogrid/commit/c5be059d2755e9a20ce7ed895ce528a7e0ac6844))
* **deps:** Bump pytest-cov from 7.0.0 to 7.1.0 ([#372](https://github.com/ansys/pyturbogrid/issues/372)) ([a06ae32](https://github.com/ansys/pyturbogrid/commit/a06ae320c22a998fe49ee84465096ec7cba2100c))
* **deps:** Bump sphinx-gallery from 0.20.0 to 0.21.0 ([#386](https://github.com/ansys/pyturbogrid/issues/386)) ([6050822](https://github.com/ansys/pyturbogrid/commit/6050822f2e116cd16d4406166708245a8e76abdc))

## [0.6.0](https://github.com/ansys/pyturbogrid/compare/v0.5.7...v0.6.0) (2026-04-21)


### Features

* Allow gtm file format ([#379](https://github.com/ansys/pyturbogrid/issues/379)) ([ee9f1c5](https://github.com/ansys/pyturbogrid/commit/ee9f1c53259c6ca388c923ceac3ba3ff719f1e66))


### Build System

* **deps:** Bump panel from 1.8.7 to 1.8.10 ([#366](https://github.com/ansys/pyturbogrid/issues/366)) ([c992f95](https://github.com/ansys/pyturbogrid/commit/c992f959723e436b9efd3b6033554dbfaef5f907))

## [0.5.7](https://github.com/ansys/pyturbogrid/compare/v0.5.6...v0.5.7) (2026-04-09)


### Bug Fixes

* Move imports into methods so as not to require fabric ([#375](https://github.com/ansys/pyturbogrid/issues/375)) ([90a7155](https://github.com/ansys/pyturbogrid/commit/90a7155be2d9c6c0db805dcd1ce55ac77dc8442c))


### Build System

* **deps:** Bump deepdiff from 8.6.1 to 8.6.2 ([#362](https://github.com/ansys/pyturbogrid/issues/362)) ([c575150](https://github.com/ansys/pyturbogrid/commit/c57515025e59373e359dfab0c2690ec23f5a12be))
* **deps:** Bump docker/login-action from 3 to 4 ([#360](https://github.com/ansys/pyturbogrid/issues/360)) ([915e6e6](https://github.com/ansys/pyturbogrid/commit/915e6e6dee3b7072a61086dfe5a61d0759168f35))

## [0.5.6](https://github.com/ansys/pyturbogrid/compare/v0.5.5...v0.5.6) (2026-03-20)


### Bug Fixes

* Move a from statement into a method to not expose including fabric ([b1c8f46](https://github.com/ansys/pyturbogrid/commit/b1c8f466d94784040aee3077ec24aaf610ca1c36))

## [0.5.5](https://github.com/ansys/pyturbogrid/compare/v0.5.4...v0.5.5) (2026-03-19)


### Bug Fixes

* Dependabot not picking up tg-api ([19e2cc1](https://github.com/ansys/pyturbogrid/commit/19e2cc19433d8d0be1bfb4050c0b8c0b89ee141f))
* Enable release please, fix dependabot ([b4b7ab7](https://github.com/ansys/pyturbogrid/commit/b4b7ab76d3d7268c83d0279f1d9107d4a5cfd097))
* Restore tests, note it is using 252 ([bebaa8d](https://github.com/ansys/pyturbogrid/commit/bebaa8dde31349555b11b98e7d9a6b862efbc1b1))
* Update launcher version for 271 ([44dde23](https://github.com/ansys/pyturbogrid/commit/44dde2304b5aaf104f59b7690f85cbe12c38f52e))
* Use repo scope action for repo tagging until ansys actions has it ([7624cee](https://github.com/ansys/pyturbogrid/commit/7624cee8d6b5a77891be5598be7531d9d54b70b0))


### Build System

* **deps:** Bump ansys-turbogrid-api from 0.5.5 to 0.7.4 ([#369](https://github.com/ansys/pyturbogrid/issues/369)) ([f8c2832](https://github.com/ansys/pyturbogrid/commit/f8c2832ce1e72289dcb2bac3bbbd836bf92e5d9d))

## CHANGELOG
