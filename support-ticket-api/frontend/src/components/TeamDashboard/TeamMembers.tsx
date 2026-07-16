import type { TeamMember } from '../types/team';
import { Card, CardHeader, CardBody } from '../shared/Card';
import Avatar from '../shared/Avatar';
import Badge from '../shared/Badge';
import { MoreHorizontal, Mail, CheckCircle } from 'lucide-react';

interface TeamMembersProps {
  members: TeamMember[];
  onMemberClick?: (member: TeamMember) => void;
}

const roleColors = {
  admin: 'danger',
  manager: 'warning',
  developer: 'primary',
  designer: 'info',
  qa: 'success',
} as const;

export default function TeamMembers({ members, onMemberClick }: TeamMembersProps) {
  const onlineCount = members.filter(m => m.status === 'online').length;

  return (
    <Card padding="none">
      <CardHeader className="px-5 pt-5">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Team Members</h2>
          <p className="text-sm text-gray-500 mt-1">
            {onlineCount} of {members.length} online
          </p>
        </div>
        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
          <MoreHorizontal className="w-5 h-5 text-gray-400" />
        </button>
      </CardHeader>
      <CardBody>
        <div className="divide-y divide-gray-100">
          {members.map((member) => (
            <div
              key={member.id}
              onClick={() => onMemberClick?.(member)}
              className="flex items-center gap-4 px-5 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <Avatar
                name={member.name}
                size="md"
                status={member.status}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-gray-900 truncate">{member.name}</h3>
                  <Badge variant={roleColors[member.role]} size="sm">
                    {member.role}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500 truncate">{member.department}</p>
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1" title="Tasks completed">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>{member.tasksCompleted}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    window.location.href = `mailto:${member.email}`;
                  }}
                  className="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
                  title="Send email"
                >
                  <Mail className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
