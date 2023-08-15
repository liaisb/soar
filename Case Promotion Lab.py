"""

"""


import phantom.rules as phantom
import json
from datetime import datetime, timedelta


@phantom.playbook_block()
def on_start(container):
    phantom.debug('on_start() called')

    # call 'compose_report' block
    compose_report(container=container)

    return

@phantom.playbook_block()
def compose_report(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("compose_report() called")

    template = """A file has been detected that has been determined to be potentially malicious. A case has been opened.\n- **Case link**: {0}\n- **Event Name**: {1}\n- **Description**: {2}\n- **Source URL**: {3}\n- **Target Server IP**: {4}\n- **Suspicious File Path**: {5} \n- **Reason for promotion**: {6}"""

    # parameter list for template variable replacement
    parameters = [
        "container:url",
        "container:name",
        "a",
        "",
        "",
        "",
        ""
    ]

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.format(container=container, template=template, parameters=parameters, name="compose_report")

    add_comment_add_note_promote_to_case(container=container)

    return


@phantom.playbook_block()
def add_comment_add_note_promote_to_case(action=None, success=None, container=None, results=None, handle=None, filtered_artifacts=None, filtered_results=None, custom_function=None, **kwargs):
    phantom.debug("add_comment_add_note_promote_to_case() called")

    compose_report = phantom.get_format_data(name="compose_report")

    ################################################################################
    ## Custom Code Start
    ################################################################################

    # Write your custom code here...

    ################################################################################
    ## Custom Code End
    ################################################################################

    phantom.promote(container=container, template="Data Breach")
    phantom.comment(container=container, comment="Promoted to Case")
    phantom.add_note(container=container, content=compose_report, note_format="markdown", note_type="general", title="Incident Report")

    container = phantom.get_container(container.get('id', None))

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