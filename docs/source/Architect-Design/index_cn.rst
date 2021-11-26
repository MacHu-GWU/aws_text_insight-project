首先我们定义一些术语, 以便描述.

- 类文本文件: 包括 纯文本, 富文本, Word, PDF, Image, Html 等. 当然 Image 指的是文本的扫描件, 纯图片不算.

**首先我们来确定一下目标**:

**商业目标**:

1. 从类文本文件中提取数据, 降低人类阅读的工作量, 提高效率.
2. 对这些提取出来的数据进行清洗, 分析, 以提供商业洞察和帮助商业决策.
3. 建造一个管道, 自动化完成数据收集, 处理, 分析, 决策, 提高效率和创造价值.

**技术目标**:

1. 从非结构化的, 类文本文件中提取文本和数据.
2. 将这些原始文本以及提取后的结构化数据以一种方便查询和分析的方式存储起来.
3. 可以同时处理大量文件流.
4. 可以兼容分析和报表工具.

**然后我们分析一下具体的技术需求**

1. 将类文本转化为 纯文本 或 富文本. 因为任何文本挖掘工具都是基于文本输入的. 所以第一步就要将 Word, PDF, Image, Html 这一类的文件转化为文本.

    对于 图片 和 PDF, AWS 有一个服务叫做 `Textract <https://docs.aws.amazon.com/textract/latest/dg/what-is.html>`_, 可以实现高质量的图片转文本.

2. 对纯文本进行 AI 分析, 从中提取数据. 包括 有特征的数据, 例如 电话号码, email, 地址, 日期; 有含义的数据, 例如 人名, 地名, 物品名; 有价值的数据, 例如 金额, 数字, 表格 等.

    AWS 有一个服务叫做 `Comprehend <https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html>`_, 可以用 AI 扫描文本, 标记里面的 Entity, 抽取结构化的数据.

3. 我们需要方便地查询和分析处理后的文本文件, 以及提取后的数据文件. 这点可以用 Elastic Search 进行索引, 查询.
4. 而具体的分析工具有很多, 例如 Kibana 可以可视化 ES, Athena 允许用 SQL 查询, Quicksight 可以生成报表.
5. 这其中的计算由于是以单个文件为输入单位, 一个文件的大小通常是可控的, 不会太夸张. 所以用事件触发的模式 + AWS Lambda 来实现计算模块是最优的.
6. 对每个文件的处理流程很长, 步骤很多, 所以我们需要用 Dynamodb 来保存状态数据, 记录每一个文件到哪一步了.
7. 我们需要保存很多中等大小 (100KB - 500MB) 的文件, 纯文本数据, 结构化的数据. AWS S3 是最佳选择.

**管道工作流**

1. 原始数据被上传到 S3
2. 触发 AWS Lambda, 将原始文件移动到被设计过的 S3 Location. 并调用 Textract 或是 Python 函数, 将文件转化为文本.


1. 原始文件被上传到 S3 ``Landing``.

    在这一步中, 原文件被上传到 S3. 如果这个上传动作是人类手动的, 那么则无法避免覆盖已存在的文件, 除非启用 S3 Object Version, 但是如果启用 Version, 会导致整个 App 的复杂程度大幅上升. 当然还可以使用一个上传代理, 上传前计算文件的 md5, 把 md5 作为 Key, 确保 S3 Key 绝对不会重复.

    最终这一步我们的解决方案是, 允许用户随意上传, 也允许用上传代理. 文件一旦被上传就立刻在下一步骤的 AWS Lambda 里进行复制, 并把 md5 作为 Key 放在一个叫做 ``Source`` 的 prefix 下面.

    S3 Structure::

        s3://landing-bucket/prefix/filename

2. 把 ``Landing`` 里的文件拷贝到 ``Source``

    上传到 ``Landing`` 中的文件触发一个 Lambda Function 进行处理. 将文件拷贝到 ``Source`` 的位置, 并用 etag 作为 Key 的一部分.

    S3 Structure::

        s3://source-bucket/prefix/${etag}/file.dat




- Upload to S3: ``s3://text-insight-landing-bucket/...``
- Copy and rename the original data to: ``s3://text-insight-original-bucket/data/a1b2c3d4.dat``, data type stored in metadata.
- Copy and rename the original data to:
    - for pure text, word ``s3://text-insight-pure-text-bucket/data/a1b2c3d4/text.txt``
    - for PDF, image that need Textract::

        # textract output
        s3://text-insight-pure-text-bucket/data/a1b2c3d4/4f1d4359e8ddd169f4f0baa5ee886203/1
        s3://text-insight-pure-text-bucket/data/a1b2c3d4/4f1d4359e8ddd169f4f0baa5ee886203/2
        ...
        s3://text-insight-pure-text-bucket/data/a1b2c3d4/4f1d4359e8ddd169f4f0baa5ee886203/9

        # merge to
        s3://text-insight-pure-text-bucket/data/a1b2c3d4/text.txt



运维:

我们一共分三个环境 ``dev``, ``test``, ``prod``.

- 开发者在本地电脑上开发, 执行 pytest, 以及用 chalice deploy 部署, 都是: ``dev`` 环境
- 开发者在本地电脑上执行 ``pytest``: ``test`` 环境
- 开发者用 chalice deploy 部署:
