"""

"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'locate_source' block
    locate_source(container=container)
    # call 'source_reputation' block
    source_reputation(container=container)
    # call 'virus_search' block
    virus_search(container=container)
    # call 'playbook_log_file_hashes_1' block
    playbook_log_file_hashes_1(container=container)

    return

@phantom.playbook_block()
def locate_source(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("locate_source() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceAddress","artifact:*.id"])

    parameters = []

    # build parameters list for 'locate_source' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "ip": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("geolocate ip", parameters=parameters, name="locate_source", assets=["maxmind"], callback=join_check_positives)

    return


@phantom.playbook_block()
def debug_2(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("debug_2() called")

    source_reputation_result_data = phantom.collect2(container=container, datapath=["source_reputation:action_result.summary","source_reputation:action_result.parameter.context.artifact_id"], action_results=results)
    virus_search_result_data = phantom.collect2(container=container, datapath=["virus_search:action_result.summary","virus_search:action_result.parameter.context.artifact_id"], action_results=results)

    source_reputation_result_item_0 = [item[0] for item in source_reputation_result_data]
    virus_search_result_item_0 = [item[0] for item in virus_search_result_data]

    parameters = []

    parameters.append({
        "input_1": source_reputation_result_item_0,
        "input_2": virus_search_result_item_0,
        "input_3": None,
        "input_4": None,
        "input_5": None,
        "input_6": None,
        "input_7": None,
        "input_8": None,
        "input_9": None,
        "input_10": None,
    })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.custom_function(custom_function="community/debug", parameters=parameters, name="debug_2")

    return


@phantom.playbook_block()
def source_reputation(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("source_reputation() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.sourceDnsDomain","artifact:*.id"])

    parameters = []

    # build parameters list for 'source_reputation' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "domain": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("domain reputation", parameters=parameters, name="source_reputation", assets=["virustotal"], callback=join_check_positives)

    return


@phantom.playbook_block()
def virus_search(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("virus_search() called")

    # phantom.debug('Action: {0} {1}'.format(action['name'], ('SUCCEEDED' if success else 'FAILED')))

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.fileHash","artifact:*.id"])

    parameters = []

    # build parameters list for 'virus_search' call
    for container_artifact_item in container_artifact_data:
        if container_artifact_item[0] is not None:
            parameters.append({
                "hash": container_artifact_item[0],
                "context": {'artifact_id': container_artifact_item[1]},
            })

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.act("file reputation", parameters=parameters, name="virus_search", assets=["virustotal"], callback=join_check_positives)

    return


@phantom.playbook_block()
def join_check_positives(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("join_check_positives() called")

    if phantom.completed(action_names=["locate_source", "source_reputation", "virus_search"]):
        # call connected block "check_positives"
        check_positives(container=container, handle=handle)

    return


@phantom.playbook_block()
def check_positives(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("check_positives() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["virus_search:action_result.summary.positives", ">", 10]
        ],
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        source_country_filter(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'else' condition 2
    format_1(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def notify_soc_management(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("notify_soc_management() called")

    # set user and message variables for phantom.prompt call

    user = container.get('owner_name', None)
    role = None
    message = """A potentially malicious file download has been detected on a local server with IP address {0}"""

    # parameter list for template variable replacement
    parameters = [
        "artifact:*.cef.destinationAddress"
    ]

    # responses
    response_types = [
        {
            "prompt": "Notify SOC management?",
            "options": {
                "type": "list",
                "choices": [
                    "Yes",
                    "No"
                ],
            },
        },
        {
            "prompt": "Reason for Decision",
            "options": {
                "type": "message",
            },
        }
    ]

    phantom.prompt2(container=container, user=user, role=role, message=message, respond_in_mins=1, name="notify_soc_management", parameters=parameters, response_types=response_types, callback=evaluate_prompt)

    return


@phantom.playbook_block()
def evaluate_prompt(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("evaluate_prompt() called")

    # check for 'if' condition 1
    found_match_1 = phantom.decision(
        container=container,
        conditions=[
            ["notify_soc_management:action_result.status", "!=", "success"]
        ],
        delimiter=None)

    # call connected blocks if condition 1 matched
    if found_match_1:
        pin_add_to_comment(action=action, success=success, container=container, results=results, handle=handle)
        return

    # check for 'elif' condition 2
    found_match_2 = phantom.decision(
        container=container,
        conditions=[
            ["notify_soc_management:action_result.summary.responses.0", "==", "Yes"]
        ],
        delimiter=None)

    # call connected blocks if condition 2 matched
    if found_match_2:
        return

    # check for 'else' condition 3
    add_comment_set_status_1(action=action, success=success, container=container, results=results, handle=handle)
    promote_to_case(action=action, success=success, container=container, results=results, handle=handle)

    return


@phantom.playbook_block()
def format_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("format_1() called")

    template = """Virus positives {0} are below threshold 10, closing event.\n"""

    # parameter list for template variable replacement
    parameters = [
        "virus_search:action_result.status"
    ]

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="format_1")

    add_comment_set_status(container=container)

    return


@phantom.playbook_block()
def add_comment_set_status(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("add_comment_set_status() called")

    format_1 = phantom.get_format_data(name="format_1")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.comment(container=container, comment=format_1)
    phantom.set_status(container=container, status="closed")

    container = phantom.get_container(container.get('id', None))

    return


@phantom.playbook_block()
def pin_add_to_comment(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("pin_add_to_comment() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.pin(container=container, message="Awaiting Action", name="Awaiting Action", pin_style="red", pin_type="card")
    phantom.comment(container=container, comment="User failed to promote event within time limit")

    return


@phantom.playbook_block()
def add_comment_set_status_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("add_comment_set_status_1() called")

    notify_soc_management_result_data = phantom.collect2(container=container, datapath=["notify_soc_management:action_result.summary.responses.1"], action_results=results)

    notify_soc_management_summary_responses_1 = [item[0] for item in notify_soc_management_result_data]

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.comment(container=container, comment=notify_soc_management_summary_responses_1)
    phantom.set_status(container=container, status="closed")

    container = phantom.get_container(container.get('id', None))

    return


@phantom.playbook_block()
def promote_to_case(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("promote_to_case() called")

    notify_soc_management_result_data = phantom.collect2(container=container, datapath=["notify_soc_management:action_result.summary.responses.1"], action_results=results)

    notify_soc_management_summary_responses_1 = [item[0] for item in notify_soc_management_result_data]

    inputs = {
        "promotion_reason": notify_soc_management_summary_responses_1,
    }

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    # call playbook "https://github.com/liaisb/soar.git/Case Promotion Lab", returns the playbook_run_id
    playbook_run_id = phantom.playbook("https://github.com/liaisb/soar.git/Case Promotion Lab", container=container, name="promote_to_case", inputs=inputs)

    return


@phantom.playbook_block()
def source_country_filter(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("source_country_filter() called")

    # collect filtered artifact ids and results for 'if' condition 1
    matched_artifacts_1, matched_results_1 = phantom.condition(
        container=container,
        conditions=[
            ["locate_source:action_result.data.*.country_name", "not in", "custom_list:Banned Countries "]
        ],
        name="source_country_filter:condition_1",
        delimiter=None)

    # call connected blocks if filtered artifacts or results
    if matched_artifacts_1 or matched_results_1:
        notify_soc_management(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=matched_artifacts_1, filtered_results=matched_results_1)

    # collect filtered artifact ids and results for 'if' condition 2
    matched_artifacts_2, matched_results_2 = phantom.condition(
        container=container,
        conditions=[
            ["locate_source:action_result.data.*.country_name", "in", "custom_list:Banned Countries "]
        ],
        name="source_country_filter:condition_2",
        delimiter=None)

    # call connected blocks if filtered artifacts or results
    if matched_artifacts_2 or matched_results_2:
        add_comment_set_status_5(action=action, success=success, container=container, results=results, handle=handle, filtered_artifacts=matched_artifacts_2, filtered_results=matched_results_2)

    return


@phantom.playbook_block()
def add_comment_set_status_5(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("add_comment_set_status_5() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.comment(container=container, comment="Hi positives but low risk source")
    phantom.set_status(container=container, status="closed")

    container = phantom.get_container(container.get('id', None))

    return


@phantom.playbook_block()
def playbook_log_file_hashes_1(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("playbook_log_file_hashes_1() called")

    container_artifact_data = phantom.collect2(container=container, datapath=["artifact:*.cef.fileHash"])

    container_artifact_cef_item_0 = [item[0] for item in container_artifact_data]

    inputs = {
        "hash": container_artifact_cef_item_0,
    }

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    # call playbook "https://github.com/liaisb/soar.git/Log File Hashes", returns the playbook_run_id
    playbook_run_id = phantom.playbook("https://github.com/liaisb/soar.git/Log File Hashes", container=container, inputs=inputs)

    return


@phantom.playbook_block()
def on_finish(container, summary):
    phantom.debug("on_finish() called")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    return