BloomFilter的原理
===
BloomFilter的算法描述
空bloom filter是m位的位数组，全部设置为0。还必须定义k个不同的散列函数，
每个散列函数将一些集合元素映射或散列到m个阵列位置之一，从而生成均匀的随机分布。
通常， k是常数，远小于m，其与要添加的元素的数量成比例; k的精确选择和m的比例常数由过滤器的预期误报率决定。

要添加元素，请将其提供给每个k哈希函数以获取k个数组位置。将所有这些位置的位设置为1。

要查询元素（匹配它是否在集合中，请将其提供给每个k哈希函数以获取k个数组位置。
如果这些位置的任何位为0，则该元素肯定不在该集合中 - 如果是，则插入时所有位都将设置为1。
如果全部都是1，则元素在集合中，或者在插入其他元素期间偶然将位设置为1，从而导致误报。

虽然存在误报问题，但BloomFilter比其他数据结构具有强大的空间优势。
大部分数据结构（如：平衡二叉树，前缀树，哈希表）都要求至少存储数据项本身，或者数据的一部分。
但是，BloomFilter根本不存储数据项。相比之下，具有1％误差和最佳值k的布隆过滤器每个元素仅需要大约9.6比特，
而不管元素的大小。这种优势部分来自于其紧凑性，继承自阵列，部分来自其概率性质。
通过每个元素仅添加约4.8位，可以将1％的误报率降低10倍。

误报的可能性
假设散列函数以相等的概率选择每个阵列位置。

如果m是数组中的位数，则在插入元素期间某个散列函数未将某个位设置为1的概率是
![$1-{\frac {1}{m}}$](https://latex.codecogs.com/gif.latex?1-{\frac{1}{m}})
如果k是散列函数的数量并且彼此之间没有显着的相关性，那么任何散列函数未将该位设置为1的概率是 ![$\left(1-{\frac {1}{m}}\right)^{k}$](https://latex.codecogs.com/gif.latex?\left(1-{\frac{1}{m}}\right)^{k})

如果我们插入了n个元素，那么某个位仍为0的概率就是
![${\displaystyle \left(1-{\frac {1}{m}}\right)^{kn}}$](https://latex.codecogs.com/gif.latex?(1-{\frac{1}{m}})^{kn})

因此，它是1的概率
![${\displaystyle 1-\left(1-{\frac {1}{m}}\right)^{kn}}$](https://latex.codecogs.com/gif.latex?1-(1-{\frac{1}{m}})^{kn})
现在测试不在集合中的元素的成员资格。由散列函数计算的每个k个阵列位置是1，概率如上。
所有这些都是1的概率，这将导致算法错误地声称该元素在集合中，通常作为
![${\displaystyle \left(1- \left[1-{\frac {1}{m}} \right]^{kn} \right)^{k}\approx \left(1-e^{-kn/m} \right)^{k}}$](https://latex.codecogs.com/gif.latex?E[q]=\left(1-\left[1-{\frac{1}{m}}\right]^{kn}\right)^{k}\approx\left(1-e^{-kn/m}\right)^{k})
这不是严格正确的，因为它假定每个位被设置的概率是独立的。

然而，假设它是近似的，我们假设误差的概率随着m （阵列中的位数）的增加而减小，
并且随着n （插入的元素的数量）的增加而增加。

Mitzenmacher和Upfal给出了另一种分析方法，该方法在不假设独立性的情况下达到了相同的近似值。
将所有n个项添加到布隆过滤器后，令q为设置为0的m位的一部分，即，仍设置为0的位数为qm。
然后，在测试时不在集合中的元素的成员资格，对于由任何k个散列函数给出的数组位置，该位被设置为1的概率是1-q中。
因此，所有k个散列函数将其位设置为1的概率是 ![$(1-q)^k$](https://latex.codecogs.com/gif.latex?(1-q)^k)。
此外，q的期望值是对于n个项中的每一个，由k个散列函数中的每一个保持给定阵列位置不被触及的概率，这是（如上所述）

![${\displaystyle E[q] = \left(1-{\frac {1}{m}} \right)^{kn}}$](https://latex.codecogs.com/gif.latex?E[q]=(1-{\frac{1}{m}})^{kn})

在没有独立性假设的情况下，可以证明q非常强烈地集中在其预期值附近。
特别是，从Azuma-Hoeffding不等式 ，他们证明了 ![${\displaystyle \Pr(\left|q-E[q]\right|\geq {\frac {\lambda }{m}})\leq 2\exp(-2\lambda ^{2}/kn)}$](https://latex.codecogs.com/gif.latex?\Pr(\left|q-E[q]\right|\geq{\frac{\lambda}{m}})\leq2\exp(-2\lambda^{2}/kn))

因此，我们可以说误报的确切概率是
![${\displaystyle \sum _{t}\Pr(q=t)(1-t)^{k}\approx (1-E[q])^{k} = \left(1- \left[1-{\frac {1}{m}} \right]^{kn} \right)^{k}\approx \left(1-e^{-kn/m} \right)^{k}}$](https://latex.codecogs.com/gif.latex?\sum_{t}\Pr(q=t)(1-t)^{k}\approx(1-E[q])^{k}=\left(1-\left[1-{\frac{1}{m}}\right]^{kn}\right)^{k}\approx\left(1-e^{-kn/m}\right)^{k})
像之前一样。

布隆过滤器是一种紧凑表示一组项目的方法。通常尝试计算两组之间的交集或并集的大小。
布隆过滤器可用于近似交集的大小和两组的并集。Swamidass＆Baldi（2007）表明，对于长度为m的两个Bloom滤波器，它们的计数分别可以估算为

![${\displaystyle n(A^{*})=-{\frac {m}{k}}\ln \left[1-{\frac {n(A)}{m}}\right]}$](https://latex.codecogs.com/gif.latex?n(A^{*})=-{\frac{m}{k}}\ln\left[1-{\frac{n(A)}{m}}\right])

和

![${\displaystyle n(B^{*})=-{\frac {m}{k}}\ln \left[1-{\frac {n(B)}{m}}\right]}$](https://latex.codecogs.com/gif.latex?n(B^{*})=-{\frac{m}{k}}\ln\left[1-{\frac{n(B)}{m}}\right])

他们的联合的大小可以估计为：

![${\displaystyle n(A^{ *} \cup B^{ *})=-{\frac {m}{k}}\ln \left[1-{\frac {n(A \cup B)}{m}}\right]}$](https://latex.codecogs.com/gif.latex?n(A^{*}\cup%20B^{*})=-{\frac{m}{k}}\ln[1-{\frac{n(A\cup%20B)}{m}}])

那里![A\cupB](https://latex.codecogs.com/gif.latex?n(A\cupB))是两个BloomFilter中任何一个中设置为1的位数。

最后，交叉点可以估算为

![${\displaystyle n(A^{ *}\cap B^{ *})= n(A^{ *})+ n(B^{ *})- n(A^{ *}\cup B^{ *})}$](https://latex.codecogs.com/gif.latex?n(A^*%20\cap%20B^{*})=n(A^{*})+n(B^{*})-n(A^{*}%20\cup%20B^{*}))

一起使用这三个公式。

了解原理之后，我们在使用的过程中还要确定空间大小和使用的hash数量。
我们可以通过`bloom filter calculator`来计算。

- https://hur.st/bloomfilter/
- https://www.di-mgt.com.au/bloom-calculator.html
- http://www.ccs.neu.edu/home/pete/bloom-filters/calculator.html
