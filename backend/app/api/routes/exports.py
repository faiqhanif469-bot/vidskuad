"""
Export Routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/formats")
async def get_export_formats():
    """
    Get available export formats
    """
    return {
        'success': True,
        'formats': [
            {
                'id': 'premiere',
                'name': 'Adobe Premiere Pro',
                'description': 'XML project file compatible with Premiere Pro',
                'file_extension': '.xml'
            },
            {
                'id': 'capcut',
                'name': 'CapCut',
                'description': 'JSON project file for CapCut Desktop/Mobile',
                'file_extension': '.json'
            }
        ]
    }
