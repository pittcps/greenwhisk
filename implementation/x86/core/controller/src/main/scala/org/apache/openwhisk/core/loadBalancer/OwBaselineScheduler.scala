package org.apache.openwhisk.core.loadBalancer

import org.apache.openwhisk.common.{Logging, NestedSemaphore, TransactionId}
import org.apache.openwhisk.core.entity.{FullyQualifiedEntityName, InvokerInstanceId}


object OwBaselineScheduler extends CommonScheduler {

  override def scheduleFunction(activationRecord: ActivationRecord,
    invokers: IndexedSeq[InvokerEnergyHealth],
    dispatched: IndexedSeq[NestedSemaphore[FullyQualifiedEntityName]],
    stepSizes: Seq[Int])(implicit logging: Logging, transId: TransactionId): Option[(InvokerInstanceId, Boolean)] = {

    val functionHash = getFunctionHash(activationRecord.msg.user.namespace.name, activationRecord.fullyQualifiedEntityName)
    val numInvokers = invokers.size
    val step = stepSizes(functionHash % stepSizes.size)
    val fqn = activationRecord.fullyQualifiedEntityName
    val maxConcurrent = activationRecord.maxConcurrent
    val slots = activationRecord.memoryLimit
    if (numInvokers > 0) {
        val homeIndex = functionHash % numInvokers
        schedule(maxConcurrent, fqn, invokers, dispatched, slots, homeIndex, step)
      } else {
        None
      }
  }
}
