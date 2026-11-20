"""KV抢占协议的独立CPU事务；无安装、框架/GPU导入或内存分配。

Operation仅是命令，Receipt必须由真正完成事件的worker产生。本模块不把
提交、future.done、placeholder或CPU状态转换当作设备完成证明。
"""
from dataclasses import dataclass
import hashlib

TOKEN_BYTES = 42 * 2 * 2 * 128 * 2
BLOCK_TOKENS = 16


def _integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("需要范围内Python整数")
    return value


def _pages(values):
    result = tuple(values)
    if not result or any(type(x) is not int or x <= 0 for x in result):
        raise ValueError("只接受非null物理页")
    if len(set(result)) != len(result):
        raise ValueError("完整Attention页不允许重复")
    return result


def prefix_digest(tokens, count):
    _integer(count, 1)
    if len(tokens) < count:
        raise ValueError("已知token不足")
    digest = hashlib.sha256()
    for token in tokens[:count]:
        _integer(token)
        digest.update(token.to_bytes(8, "little", signed=False))
    return digest.hexdigest()


@dataclass(frozen=True)
class Key:
    session: str
    request_id: str
    incarnation: int
    attempt: int

    def __post_init__(self):
        if (not isinstance(self.session, str) or not self.session
                or not isinstance(self.request_id, str) or not self.request_id):
            raise ValueError("需要engine session和request ID")
        _integer(self.incarnation, 1)
        _integer(self.attempt, 1)


@dataclass(frozen=True)
class Snapshot:
    key: Key
    prefix_tokens: int
    token_digest: str
    source_pages: tuple[int, ...]
    pending_frames: tuple[int, ...]

    def __post_init__(self):
        if (not isinstance(self.key, Key) or type(self.source_pages) is not tuple
                or type(self.pending_frames) is not tuple or _integer(self.prefix_tokens, 16) % 16
                or len(self.source_pages) != self.prefix_tokens // 16):
            raise ValueError("snapshot只能包含完整16token页")
        _pages(self.source_pages)
        if (len(set(self.pending_frames)) != len(self.pending_frames)
                or any(type(x) is not int or x < 1 for x in self.pending_frames)
                or len(self.token_digest) != 64
                or any(x not in "0123456789abcdef" for x in self.token_digest)):
            raise ValueError("snapshot frame身份或digest不合法")

    @property
    def nbytes(self):
        return self.prefix_tokens * TOKEN_BYTES


def plan_snapshot(key, issued_tokens, known_token_ids, source_pages, queued_frames):
    """queued_frames为尚未消费的frame_seq->该请求scheduled token数。

    只保存确定完成的完整页；保留至少一个已知token用于重新取得logits。
    queued数量来自真实SchedulerOutput，绝不以输出placeholder数量替代。
    """
    _integer(issued_tokens)
    frames = tuple(queued_frames)
    if any(type(seq) is not int or seq < 1 for seq in frames):
        raise ValueError("frame必须有单调正整数身份")
    outstanding = sum(_integer(n, 1) for n in queued_frames.values())
    stable = min(issued_tokens - outstanding, len(known_token_ids) - 1)
    count = (stable // BLOCK_TOKENS) * BLOCK_TOKENS
    if count < BLOCK_TOKENS:
        raise ValueError("没有可保存的完整稳定前缀")
    pages = _pages(source_pages)
    if len(pages) < count // BLOCK_TOKENS:
        raise ValueError("实际页数小于稳定前缀")
    return Snapshot(key, count, prefix_digest(known_token_ids, count),
                    pages[:count // BLOCK_TOKENS], frames)


def split_fresh_zero_ids(before, after, private_pages, *, pending_zero=True):
    """actual SingleTypeKVCacheManager.new_block_ids只移除本次追加页。

    不调用take_new_block_ids。pending_zero=False时before是未drain历史，
    可含已释放/复用ID；只以此次实际分配尾段与私有所有权证明新页。
    返回值只是建议的新list，调用者在真实zero完成后才应用，异常不修改原list。
    """
    before, after, pages = tuple(before), tuple(after), _pages(private_pages)
    if (after[:len(before)] != before or len(after) != len(before) + len(pages)
            or set(after[len(before):]) != set(pages)
            or pending_zero and set(before).intersection(pages)):
        raise RuntimeError("fresh零页不是独占追加尾段，禁止全局drain或发布restore")
    return before, tuple(after[len(before):])


class HostSlot:
    """严格单victim的显式buffer预算；不代表整个cgroup实际峰值。"""

    def __init__(self, max_bytes):
        self.max_bytes = _integer(max_bytes, 1)
        self.key = None
        self.used_bytes = 0
        self._serial = 0

    def reserve(self, key, nbytes):
        _integer(nbytes, 1)
        if self.key is not None or nbytes > self.max_bytes:
            raise BufferError("单victim slot已占用或超过显式host预算")
        self.key, self.used_bytes = key, nbytes

    def _release(self, key):
        if self.key != key:
            raise RuntimeError("不能释放其它request epoch的slot")
        self.key, self.used_bytes = None, 0

    def _next_serial(self, key):
        if self.key != key:
            raise RuntimeError("slot与操作epoch不匹配")
        self._serial += 1
        return self._serial


@dataclass(frozen=True)
class Operation:
    key: Key
    serial: int
    kind: str
    pages: tuple[int, ...]
    nbytes: int


@dataclass(frozen=True)
class Receipt:
    operation: Operation
    transferred_bytes: int
    completed: bool
    successful: bool


class Transaction:
    """不调用allocator/RPC/future/RNG；适配器执行命令并提交真实ack。"""

    def __init__(self, snapshot, slot):
        if not isinstance(snapshot, Snapshot) or not isinstance(slot, HostSlot):
            raise TypeError("需要已规划Snapshot与单victim HostSlot")
        slot.reserve(snapshot.key, snapshot.nbytes)
        self.snapshot, self.slot = snapshot, slot
        self.phase, self.serial, self.inflight = "CREATED", 0, None
        self.pending_frames = set(snapshot.pending_frames)
        self.destination_pages = ()
        self.source_released = self.cancelled = self.closed = False

    def _active(self):
        if self.closed:
            raise RuntimeError("事务已关闭")

    def _operation(self, expected_phase, kind, pages):
        self._active()
        if self.cancelled or self.phase != expected_phase or self.inflight is not None:
            raise RuntimeError("事务阶段或cancel状态不允许提交")
        # slot生命周期内单调，连错误复用同一个Key的重试也不能接受旧ACK。
        self.serial = self.slot._next_serial(self.snapshot.key)
        self.inflight = Operation(self.snapshot.key, self.serial, kind, pages,
                                  self.snapshot.nbytes)
        self.phase = kind + "_PENDING"
        return self.inflight

    def submit_save(self):
        return self._operation("CREATED", "SAVE", self.snapshot.source_pages)

    def acknowledge(self, receipt):
        self._active()
        if (self.inflight is None or not isinstance(receipt, Receipt)
                or receipt.operation != self.inflight):
            raise RuntimeError("陈旧或异epoch/页映射的ack")
        if receipt.completed is not True:
            raise RuntimeError("提交不等于完成；保留页和host强引用")
        _integer(receipt.transferred_bytes)
        if type(receipt.successful) is not bool:
            raise ValueError("ack必须明确成功或失败")
        if receipt.successful and receipt.transferred_bytes != self.inflight.nbytes:
            raise RuntimeError("成功ack字节数不足")
        kind = self.inflight.kind
        self.inflight = None
        self.phase = "CANCELLED" if self.cancelled else (
            ("RESTORE_DONE" if kind == "RESTORE_FULL" else kind + "_DONE")
            if receipt.successful is True else "FAILED")

    def source_free_permitted(self):
        self._active()
        return not self.source_released and self.inflight is None and self.phase in (
            "SAVE_DONE", "FAILED", "CANCELLED")

    def source_free_committed(self):
        """仅在原_preempt_request/finish实际释放返回后调用，不执行free。"""
        if not self.source_free_permitted():
            raise RuntimeError("save未完成，不可确认source free")
        self.source_released = True
        if self.phase == "SAVE_DONE":
            self.phase = "HOST_RESIDENT"

    def frame_processed(self, current_key, frame_seq):
        """原update_from_output成功返回后且对象epoch匹配才调用。"""
        self._active()
        if current_key != self.snapshot.key or frame_seq not in self.pending_frames:
            raise RuntimeError("frame已处理或不属于该snapshot")
        self.pending_frames.remove(frame_seq)

    def bind_private_allocation(self, current_key, current_token_ids, pages, fresh_ids):
        """只绑定真实allocator已分配的私有页，不分配或发布prefix hit。"""
        self._active()
        if (self.phase != "HOST_RESIDENT" or self.cancelled or self.pending_frames
                or current_key != self.snapshot.key
                or len(current_token_ids) <= self.snapshot.prefix_tokens):
            raise RuntimeError("尚有旧frame/取消/epoch不匹配，走原重算")
        if prefix_digest(current_token_ids, self.snapshot.prefix_tokens) != self.snapshot.token_digest:
            raise RuntimeError("token前缀改变，禁止恢复")
        pages, fresh_ids = _pages(pages), _pages(fresh_ids)
        if len(pages) != len(self.snapshot.source_pages) or set(pages) != set(fresh_ids):
            raise RuntimeError("必须逐页拥有并消费本次完整fresh-zero集合")
        self.destination_pages, self.phase = pages, "ALLOCATED"

    def submit_zero(self):
        return self._operation("ALLOCATED", "ZERO", self.destination_pages)

    def submit_restore(self):
        return self._operation("ZERO_DONE", "RESTORE", self.destination_pages)

    def submit_restore_full(self):
        """完整私有页覆盖使用真实新操作；没有ZERO提交或伪ZERO_ACK。"""
        return self._operation("ALLOCATED", "RESTORE_FULL", self.destination_pages)

    def publish(self, current_key, current_token_ids):
        self._active()
        if (self.cancelled or self.phase != "RESTORE_DONE" or self.inflight is not None
                or self.pending_frames or current_key != self.snapshot.key):
            raise RuntimeError("restore完成及epoch/frame检查之前不可发布computed")
        if len(current_token_ids) <= self.snapshot.prefix_tokens:
            raise RuntimeError("须保留至少一个待计算token以取得logits")
        if prefix_digest(current_token_ids, self.snapshot.prefix_tokens) != self.snapshot.token_digest:
            raise RuntimeError("发布前token前缀已变")
        self.phase = "PUBLISHED"
        return {"key": self.snapshot.key, "computed_tokens": self.snapshot.prefix_tokens,
                "block_ids": self.destination_pages, "sampling_calls": 0}

    def cancel(self):
        self._active()
        self.cancelled = True
        # 发布后物理页已回归原scheduler所有权，不能再当私有rollback页。
        if self.inflight is None and self.phase != "PUBLISHED":
            self.phase = "CANCELLED"

    def discard(self):
        """预算/容量/pendingframe不适用时回原重算；不改变请求队列。"""
        self._active()
        if self.inflight is not None or self.destination_pages or self.phase == "PUBLISHED":
            raise RuntimeError("先等待传输并回滚私有分配，不可丢失所有权")
        self.phase = "DISCARDED"

    def rollback_unpublished(self):
        """后续原allocate失败/未发出工作时撤回tentative computed，不能撤已发布。"""
        self._active()
        if self.inflight is not None or self.phase not in (
                "ALLOCATED", "ZERO_DONE", "RESTORE_DONE"):
            raise RuntimeError("只允许已settle且未发布的私有前缀回滚")
        self.phase = "ROLLBACK"

    def release_private_allocation(self):
        """返回可回滚页号；适配器实际free成功后再确认，禁止inflight释放。"""
        self._active()
        if self.inflight is not None or self.phase not in ("FAILED", "CANCELLED", "ROLLBACK"):
            raise RuntimeError("仅完成/失败已settle后可回滚，不能发布半恢复页")
        return self.destination_pages

    def private_allocation_released(self):
        self.release_private_allocation()
        self.destination_pages = ()

    def close(self):
        self._active()
        if (self.inflight is not None or self.phase not in (
                "PUBLISHED", "FAILED", "CANCELLED", "DISCARDED", "ROLLBACK")
                or self.destination_pages and self.phase != "PUBLISHED"):
            raise RuntimeError("传输或私有页仍在使用，不能释放host slot")
        self.slot._release(self.snapshot.key)
        self.closed = True
