"""
Application Permissions
"""
UserPermissions = [
    'view_user',
    'edit_user',
    'delete_user',
    'add_user',
    'list_users',
    'view_user',
    'update_profile'
]

TeamPermissions = [
    'list_teams',
    'create_team',
    'edit_team',
    'delete_team',
    'remove_team_members',
    'import_users',
    'send_assessment_to_team'
]

TeamMembersPermissions = [
    "create_members",
    "list_members",
    "remove_member"
]

AssessmentPermissions = [
    'check_assessment_eligibility',
    'check_assessment_eligibility',
    'get_assessment_question',
    'submit_assessment_question',
    'finish_assessment'
]

Permissions = {
    'super_admin': [
        *UserPermissions,
        *TeamPermissions,
        *TeamMembersPermissions[1:],
        'view_all'
    ],
    'company': [
        *UserPermissions[3:],
        *TeamPermissions,
        *TeamMembersPermissions,
        'view_profile',
        'view_team_assessment',  # team assessment
        'view_team_assessment_result'  # team assessment
    ],
    'educator': [
        UserPermissions[6],
        *AssessmentPermissions,
        'view_users',
        'view_assessment',  # single assessment
        'get_assessment',  # single assessment
        'view_assessment_result',  # single assessment
    ],
    'candidate': [
        UserPermissions[6],
        *AssessmentPermissions,
        'view_assessment',  # single assessment
        'get_assessment',  # single assessment
        'view_assessment_result',  # single assessment
    ],
}
