# Sharoobi FileShare

الخطة التنفيذية الشاملة والعميقة لبناء نظام مشاركة وتوزيع ملفات محلي قابل للبيع والتخصيص

## 1. الرؤية

الهدف هو بناء نظام محلي احترافي لإدارة وتوزيع الملفات والبرامج والتعاريف والتحديثات داخل الشبكات المحلية، بحيث يخدم:

- مقدمين الدعم الفني والتقني
- محلات الصيانة والبرمجة
- مقاهي الإنترنت
- شبكات المؤسسات الصغيرة والمتوسطة
- مسؤولي الشبكات
- مزودي الخدمات الذين يريدون منتجاً قابلاً لإعادة التخصيص

النظام ليس مجرد `Shared Folder`.
النظام يجب أن يكون منصة تشغيل وتوزيع وإدارة ومراقبة وتحكم.

## 2. النتيجة النهائية المطلوبة

نريد منتجاً يعمل محلياً على جهاز رئيسي أو سيرفر داخل الشبكة، ويقدم:

- وصول ملفات من أجهزة ويندوز وهواتف وأجهزة أخرى
- مشاركة عبر أكثر من بروتوكول حسب الحاجة
- صلاحيات دقيقة جداً
- سرعة عالية داخل LAN
- إحصائيات تفصيلية
- تحكم بالسرعة والمستخدمين والأجهزة
- لوحة إدارة قوية
- سجل نشاط شامل
- دعم توزيع الملفات فقط أو التثبيت التلقائي
- دعم التخصيص التجاري والهوية البصرية
- قابلية فصل كل عميل أو جهة في Tenant مستقل لاحقاً

## 3. مبدأ التصميم الصحيح

لا نبني النظام على مشاركة SMB التقليدية فقط.

نستخدم بنية متعددة الطبقات:

1. طبقة تخزين
2. طبقة وصول للملفات
3. طبقة إدارة وصلاحيات
4. طبقة مراقبة وإحصاءات
5. طبقة Agent للأجهزة العميلة
6. طبقة شبكية وسياسات أداء

هذا هو الفرق بين:

- مشاركة منزلية بسيطة
- منتج حقيقي قابل للبيع

## 4. القرار المعماري الأساسي

### 4.1 ما لن نعتمد عليه

- `Jellyfin` ليس مناسباً كنواة النظام
- `SMB only` ليس كافياً
- مشاركة `H:\` بالكامل مباشرة ليست ممارسة صحيحة

### 4.2 ما سنعتمد عليه

المنتج سيُبنى على:

- `SFTPGo`
  - للوصول عبر WebDAV / HTTP / SFTP
  - للـ quotas
  - للـ bandwidth limits
  - للـ users / groups / virtual folders
  - للأحداث وواجهة الإدارة الأولية و API
- `Samba`
  - للوصول من ويندوز عبر SMB داخل LAN
  - للاستخدامات التي تحتاج Explorer و UNC paths
- `PostgreSQL`
  - لتخزين بيانات النظام والإحصائيات والسياسات
- `Redis`
  - للمهام والطوابير والكاش
- `Backend API`
  - `FastAPI` هو الأنسب حالياً
- `Frontend Admin`
  - `Next.js` أو `React`
- `Windows Agent`
  - للتثبيتات الصامتة
  - لجمع معلومات الأجهزة
  - لتنفيذ مهام install-only
- `Reverse Proxy`
  - `Caddy` أو `Traefik`
  - يفضل `Caddy` لسهولة الإعداد داخل LAN

## 5. النطاق الوظيفي للمنتج

### 5.1 السيناريوهات الأساسية

- فني يفتح مكتبة تعريفات وبرامج من جهاز عميل
- عميل Guest يدخل مكتبة عامة فقط
- جهاز مُدار يسحب تعريفات أو حزمة تثبيت تلقائياً
- مدير شبكة يراقب من نسخ ماذا ومتى
- صاحب محل يحدد لكل فرع أو لكل موظف ما يراه وما لا يراه
- مسؤول يحدد سرعة كل جهاز أو مجموعة
- مسؤول يشغّل Job تثبيت على أجهزة محددة

### 5.2 أنماط الوصول

- SMB
- WebDAV
- HTTPS direct downloads
- Share links مؤقتة
- Agent pull jobs
- Agent install jobs
- لاحقاً: API clients

## 6. المتطلبات الأساسية للنسخة الناجحة

### 6.1 المتطلبات التقنية

- Local-first
- Docker-based
- منفصل تماماً عن Stack خدماتك الحالي
- تخزين على `H:\`
- دعم 1 إلى 50 جهاز كبداية
- أداء مستقر مع ملفات كبيرة
- سجل نشاط كامل
- عدم الاعتماد على Guest المفتوح

### 6.2 المتطلبات الإدارية

- Users
- Roles
- Groups
- Devices
- Shares
- Jobs
- Policies
- Bandwidth profiles
- Audit logs
- Dashboard

### 6.3 المتطلبات التجارية

- White-label لاحقاً
- Profiles جاهزة حسب نوع العميل
- إعداد سهل
- تصدير نسخة احتياطية للإعدادات
- دعم نسخ المشروع بين العملاء
- إمكانية بيع Basic / Pro / Enterprise

## 7. هيكل المشروع على القرص H

المشروع نفسه يبقى على `H:\Sharoobi_FileShare`، أما المحتوى المشارك فيبقى في مساراته الأصلية مثل `H:\` أو أي مجلد تختاره.

الهيكل المقترح:

```text
H:\
  Sharoobi_FileShare\
    storage\
      runtime\
        agent-drop\
        bridge-cache\
        exports\
      logs\
        access\
        jobs\
        audit\
      db_backups\
      sftpgo\
    docs\
    agent\
    backend\
    frontend\
    infra\
```

### 7.1 لماذا هذا الهيكل

- يمنع الفوضى
- يفصل ملفات المشروع عن الملفات التي ستتم مشاركتها
- يترك البيانات الأصلية في مساراتها الحقيقية
- يجعل Host Bridge مسؤولاً عن ربط المسارات المحلية بالنظام

## 8. تصميم المشاركات Shares

النظام لا ينشئ مكتبات داخلية للملفات. النظام يسجل مسارات حقيقية موجودة أصلاً على الجهاز ويطبق عليها سياسات وصول وإدارة.

أمثلة مشاركات:

- `H:\`
- `H:\Office\2024`
- `H:\driver`
- `D:\Share`
- أي مجلد محدد يحتاجه الفني أو العميل

كل Share تملك:

- اسم
- وصف
- مسار جذري
- نوع الوصول
- إخفاء أو إظهار
- صلاحيات
- bandwidth policy
- visibility policy
- audit policy

## 9. نموذج الصلاحيات

### 9.1 الأدوار الأساسية

- `Super Admin`
- `Admin`
- `Technician`
- `Operator`
- `Guest`
- `Managed Device`
- `Reseller`

### 9.2 الصلاحيات الدقيقة

لكل User أو Group أو Device:

- View library
- Browse folders
- Download files
- Upload files
- Delete files
- Rename files
- Generate links
- Execute install job
- Read statistics
- Manage users
- Manage devices
- Manage policies

### 9.3 مستويات الوصول للملفات

- `Read Only`
- `Read + Download`
- `Read + Upload`
- `Full`
- `Install-Only via Agent`

### 9.4 ملاحظة مهمة

ميزة "يفتح الملف للتثبيت فقط بدون نسخه" لا يمكن ضمانها إذا أعطيت المستخدم وصول قراءة مباشر للملف.

الحل الصحيح:

- Agent على الجهاز العميل
- Job من السيرفر
- تنزيل مؤقت
- تشغيل صامت
- حذف أو تنظيف بعد التنفيذ

هذه الميزة يجب أن تُنفذ عبر `Execution Layer` وليس عبر File Share عادي.

## 10. تصميم الوصول Access Layer

### 10.1 SMB

نستخدمه فقط للسيناريوهات التالية:

- أجهزة ويندوز داخل LAN
- تصفح سريع من Explorer
- نسخ ملفات مباشر
- الفنيين داخل الشبكة

### 10.2 WebDAV / HTTPS

نستخدمه من أجل:

- تحكم أفضل بالـ auth
- ضبط السرعة
- logging
- سهولة التكامل
- دعم أجهزة وأنظمة متعددة

### 10.3 SFTP

يُستخدم للحالات التقنية أو للنسخ الآمن من أدوات خارجية أو من لينكس.

### 10.4 Agent Pull

الأفضل للتثبيتات والإدارة والسياسات والتنفيذ.

## 11. تصميم الشبكة

### 11.1 مبدأ الشبكة

النظام محلي، لكن ليس معناه أن كل شيء يجب أن يكون مفتوحاً لكل الواجهات.

سيتم اعتماد:

- VLAN أو SSID مخصص للخدمة لاحقاً إن لزم
- Binding مضبوط للخدمات
- عزل بين واجهة الإدارة وواجهة الوصول

### 11.2 مخطط الوصول المقترح

- `Admin UI`: منفذ داخلي محدود
- `Client UI / Web Access`: منفذ مستقل
- `SMB`: داخل LAN فقط
- `SFTP`: اختياري
- `API`: داخلي أو للمشرفين فقط
- `Agent API`: منفصل منطقياً

### 11.3 التوافق مع MikroTik

النسخة المتقدمة يجب أن تدعم لاحقاً:

- IP lists
- Queue trees
- Simple queues
- Dynamic policies per user/device
- WAN/LAN shaping

لكن هذه مرحلة لاحقة، وليست شرط MVP.

## 12. التحكم بالسرعة

### 12.1 مستويات التحكم

التحكم بالسرعة سيكون على 3 مستويات:

1. مستوى التطبيق
2. مستوى المستخدم أو الجهاز
3. مستوى الشبكة

### 12.2 كيف ننفذه

- داخل `SFTPGo`: per-user / per-group bandwidth limits
- داخل `Backend`: policies منطقية
- داخل الشبكة لاحقاً:
  - MikroTik integration
  - per-IP shaping

### 12.3 أمثلة سياسات

- Guest = 10 MB/s
- Technician = 80 MB/s
- Managed Devices = 40 MB/s
- شبكات معينة = سقف جماعي

## 13. تصميم الإحصائيات والـ Audit

النظام يجب أن يسجل:

- من دخل
- من أي IP
- من أي جهاز
- ما الذي تم فتحه
- ما الذي تم تنزيله
- ما الذي تم رفعه
- ما الذي تم نسخه
- حجم النقل
- مدة النقل
- متوسط السرعة
- حالات الفشل
- نتائج Jobs
- نتائج التثبيت
- عدد مرات الاستخدام لكل Library

### 13.1 الإحصائيات المطلوبة

- Top files
- Top users
- Top devices
- Total transferred by day/week/month
- Install success rate
- Failed jobs
- Active sessions
- Concurrent clients
- Average job duration

### 13.2 مصادر البيانات

- SFTPGo event logs
- SMB open files / sessions
- Agent reports
- API logs
- System metrics

## 14. تصميم الأجهزة Devices

كل جهاز عميل يجب أن يكون كياناً مستقلاً داخل النظام.

### 14.1 بيانات الجهاز

- Device ID
- Hostname
- OS version
- IP / MAC
- User owner
- Group
- Last seen
- Installed agent version
- Current policy
- Transfer stats
- Install history

### 14.2 حالات الجهاز

- Online
- Idle
- Busy
- Offline
- Blocked
- Limited

## 15. الـ Agent

الـ Agent هو مفتاح التميز التجاري الحقيقي.

### 15.1 مهامه

- تسجيل الجهاز
- إرسال heartbeat
- استلام أوامر
- تنزيل ملفات حسب Job
- تنفيذ silent install
- تسجيل النتيجة
- تنظيف الملفات المؤقتة
- إرسال inventory

### 15.2 الوظائف الأساسية

- `download-only`
- `install-only`
- `download-and-run`
- `driver-install`
- `office-deploy`
- `script-run`
- `verify-package`

### 15.3 لماذا هو مهم

بدونه سيبقى النظام قريباً من "مشاركة ملفات".
به يصبح "منصة توزيع وإدارة وتشغيل".

## 16. تصميم الـ Packages

الملف وحده لا يكفي.
نحتاج مفهوم `Package`.

كل Package يحتوي على:

- اسم
- إصدار
- Vendor
- Category
- Architecture
- File path
- Silent install command
- Detection rule
- Hash
- Dependencies
- Tags
- Notes

### 16.1 أمثلة

- `Office 2024`
- `Intel LAN Driver`
- `VMware Workstation`
- `7-Zip`
- `Visual C++ Runtime`

### 16.2 فوائد ذلك

- تشغيل تثبيتات تلقائية
- التحقق من الإصدار
- بناء Catalog قابل للبيع
- تكرار النشر بسهولة

## 17. المعمارية التقنية الكاملة

### 17.1 الخدمات الأساسية في Docker

- `deployhub_db`
- `deployhub_redis`
- `deployhub_sftpgo`
- `deployhub_samba`
- `deployhub_api`
- `deployhub_web`
- `deployhub_caddy`
- `deployhub_worker`
- `deployhub_agent_repo`

### 17.2 خدمات اختيارية لاحقاً

- `deployhub_prometheus`
- `deployhub_grafana`
- `deployhub_loki`
- `deployhub_minio`
- `deployhub_mikrotik_bridge`

### 17.3 الفصل عن خدماتك الحالية

إجباري:

- Compose project جديد مستقل
- Network جديدة مستقلة
- Database جديدة مستقلة
- Redis جديد مستقل
- منافذ جديدة مستقلة

## 18. المنافذ المقترحة

مبدئياً لتجنب التعارض مع Stack الحالي:

- `18443` واجهة النظام HTTPS
- `18080` API داخلي
- `19022` SFTP
- `19080` WebDAV/HTTP إذا لزم
- `1445` أو SMB عبر المضيف حسب التصميم النهائي

ملاحظة:

قد نُبقي SMB عبر خدمة ويندوز/مضيف وليس Docker إذا كانت إدارة Samba على Windows معقدة في البيئة الحالية.

## 19. قاعدة البيانات

### 19.1 الجداول الأساسية

- users
- roles
- groups
- devices
- shares
- folders
- packages
- package_versions
- share_links
- sessions
- transfer_logs
- install_jobs
- install_job_runs
- device_heartbeats
- bandwidth_policies
- audit_events
- settings

### 19.2 العلاقات المهمة

- User belongs to many groups
- Device belongs to one owner and one policy
- Library has many folders and many permission bindings
- Package belongs to one library and has many versions
- Job targets many devices

## 20. الواجهة الإدارية

### 20.1 الشاشات الأساسية

- Dashboard
- Libraries
- Packages
- Devices
- Users
- Groups
- Policies
- Transfers
- Jobs
- Audit
- Settings

### 20.2 بطاقة الجهاز

يجب أن تعرض:

- الحالة
- آخر اتصال
- السرعة الحالية
- ما تم تنزيله
- ما تم تثبيته
- السياسات المطبقة
- سجل آخر العمليات

### 20.3 بطاقة المكتبة

تعرض:

- الحجم
- عدد الملفات
- أكثر الملفات استخداماً
- عدد المستخدمين الذين يملكون صلاحية
- معدل النقل

## 21. الأداء والاعتمادية

### 21.1 هدف الأداء

داخل LAN:

- استقرار جيد حتى 50 جهاز كبداية
- دعم ملفات كبيرة
- حد أدنى من الفوضى في الـ IO

### 21.2 ممارسات الأداء

- تجنب تعريض جذر القرص كاملاً
- توزيع المحتوى داخل Libraries
- استخدام HTTP/WebDAV للأحمال المقاسة
- SMB للفنيين والاستخدام التقليدي فقط
- SSD للكاش والميتا إن أمكن لاحقاً
- قاعدة البيانات على volume منفصل
- لوجات منفصلة

### 21.3 ملاحظة مهمة بخصوص التخزين الحالي

القرص `H:` مناسب كبداية، لكن لا يجب اعتبار هذا السيرفر نسخة التخزين الوحيدة للبيانات التجارية طويلة المدى.

يفضل لاحقاً:

- نسخ احتياطي دوري
- قرص ثانوي للنسخ الاحتياطي
- أو RAID/replication

## 22. الأمان

### 22.1 مبادئ الأمان

- لا `Guest Full`
- لا `Everyone Full`
- لا مشاركة `Users` أو جذور الأقراص مباشرة
- الفصل بين Admin و Client access
- تسجيل كل حدث مهم
- روابط مؤقتة عند الحاجة
- حذف الـ Guest المفتوح الحالي من بيئة الإنتاج

### 22.2 ما سيتم حظره

- مشاركة `H:\` بالكامل بصلاحيات عامة
- مشاركة `C:\Users`
- وصول Redis وPostgres للعامة في المشروع الجديد

### 22.3 الطبقات الأمنية

- Auth
- RBAC
- Rate limits
- IP restrictions
- Audit logs
- Optional HTTPS local certificates

## 23. الخطة التنفيذية المرحلية

## المرحلة 0: التخطيط وتثبيت المعايير

المخرجات:

- اسم المشروع النهائي
- المعمارية المعتمدة
- شكل المجلدات على `H:\`
- السياسات الأساسية
- اختيار التقنية النهائية

## المرحلة 1: تأسيس البنية الأساسية

المخرجات:

- إنشاء هيكل المجلدات على `H:\Sharoobi_FileShare`
- إعداد Compose منفصل
- تشغيل:
  - Postgres
  - Redis
  - SFTPGo
  - API
  - Web
  - Caddy

## المرحلة 2: MVP للوصول والإدارة

المخرجات:

- Users / Roles / Groups
- Libraries
- Mount وربط المجلدات
- Dashboard أولي
- Access policies
- Audit logs
- Share links

## المرحلة 3: دعم SMB المنظم

المخرجات:

- Samba integration أو ربط SMB Windows مضبوط
- Shares منطقية بدل مشاركة الجذر
- صلاحيات حسب المكتبات
- اختبارات من أجهزة ويندوز

## المرحلة 4: Packages وCatalog

المخرجات:

- مفهوم Package
- Metadata
- Filters
- Categories
- Search
- Hash verification

## المرحلة 5: Windows Agent

المخرجات:

- Agent prototype
- device registration
- heartbeat
- download jobs
- install-only jobs
- result reporting

## المرحلة 6: الإحصائيات والتقارير

المخرجات:

- transfer stats
- top files
- device reports
- job reports
- customer usage reports

## المرحلة 7: النسخة القابلة للبيع

المخرجات:

- branding
- customer profiles
- export/import config
- licensing strategy
- installer package
- documentation

## 24. تعريف MVP الحقيقي

الـ MVP يجب أن يشمل:

- إدارة مستخدمين
- مكتبات
- وصول Web و SMB
- صلاحيات
- روابط مشاركة
- حدود سرعة
- Logs
- Dashboard أساسي

ولا يشترط في أول نسخة:

- Agent كامل
- MikroTik integration
- multi-tenant متقدم
- billing

## 25. نموذج البيع

### Basic

- Libraries
- Users
- SMB/Web access
- Basic logs

### Pro

- Policies
- Bandwidth limits
- Packages
- Detailed analytics
- Share links

### Enterprise

- Agent
- Install automation
- Multi-site
- Advanced audit
- Branding
- MikroTik integration

## 26. المخاطر الفعلية

- تحويل النظام إلى SMB share فقط
- فتح صلاحيات Everyone بشكل عشوائي
- عدم وجود Agent ثم توقع install-only
- ربطه مباشرة بالإنترنت
- مزج المشروع مع Stack شاروبي الحالي
- إهمال النسخ الاحتياطي
- الاعتماد على Guest

## 27. القرارات التنفيذية النهائية المقترحة

### قرار 1

المشروع سيكون Local-first فقط في النسخة الأولى.

### قرار 2

النواة الأساسية ستكون:

- `SFTPGo + FastAPI + PostgreSQL + Redis + Caddy`

### قرار 3

`Samba` سيكون إضافة توافقية داخل LAN وليس قلب النظام.

### قرار 4

ميزة install-only سيتم تنفيذها عبر `Windows Agent` فقط.

### قرار 5

المشروع سيكون منفصلاً تماماً عن `sharoobi` الحالي في Docker.

## 28. هيكل المشروع البرمجي المقترح

```text
H:\Sharoobi_FileShare\
  backend\
    api\
    worker\
    shared\
  frontend\
    admin-web\
  infra\
    docker\
    caddy\
    sftpgo\
    samba\
    scripts\
  agent\
    windows-agent\
  storage\
    repo\
    logs\
    staging\
  docs\
    architecture\
    api\
    operations\
  README.md
  MASTER_EXECUTION_PLAN.md
```

## 29. ما الذي سننفذه أولاً فعلياً بعد هذه الوثيقة

الترتيب الصحيح:

1. إنشاء هيكل المشروع والمجلدات
2. إعداد `docker-compose` مستقل
3. إعداد `H:\Sharoobi_FileShare\storage\repo`
4. تشغيل SFTPGo وربط virtual folders
5. إنشاء Backend API
6. إنشاء لوحة إدارة أولية
7. بناء نموذج Users / Libraries / Devices / Policies

## 30. التوصية النهائية

ابدأ بالمشروع كمنصة توزيع ملفات وإدارة وصول داخل LAN.
لا تحاول إدخال كل الخصائص التجارية دفعة واحدة.

أفضل طريق عملي:

- MVP قوي جداً
- ثم Package Catalog
- ثم Agent
- ثم Automation
- ثم المنتج التجاري النهائي

هذا المسار واقعي، قابل للتنفيذ، وقابل للبيع.

---

تم إعداد هذه الوثيقة كمرجع تنفيذي أساسي لمشروع `Sharoobi_FileShare`.
# Revision Note

This project is now explicitly centered on sharing existing local Windows paths already present on the host machine. It is not a backup system and it does not require moving content into internal platform libraries.

Current implementation direction:

- `shares` represent exact Windows paths such as `H:\` or `H:\Office\2024`
- Docker hosts metadata, auth, policies, jobs, and UI
- native Windows Host Bridge handles local path validation and SMB publishing
- future Windows Agent handles install-only execution and telemetry
